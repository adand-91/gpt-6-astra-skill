"""Small fail-closed file helpers."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

from .errors import SchemaError, UnsafePathError

MAX_JSON_INPUT_BYTES = 128 * 1024 * 1024


def _is_link_or_reparse(info: os.stat_result) -> bool:
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse)


def _trusted_macos_prefix(path: Path) -> Path:
    """Canonicalise only Apple's fixed root-level compatibility symlinks.

    tempfile commonly returns /var/... on macOS even though /var is the
    root-owned /private/var compatibility link.  Following arbitrary output
    ancestors would be unsafe, so the exception is deliberately allowlisted.
    """
    if sys.platform != "darwin":
        return path
    raw = os.fspath(path)
    for visible, canonical in (("/var", "/private/var"), ("/tmp", "/private/tmp"),
                               ("/etc", "/private/etc")):
        if raw != visible and not raw.startswith(visible + os.sep):
            continue
        try:
            info = os.lstat(visible)
            resolved = os.path.realpath(visible)
        except OSError:
            return path
        if stat.S_ISLNK(info.st_mode) and resolved == canonical:
            suffix = raw[len(visible):].lstrip(os.sep)
            return Path(canonical) / suffix if suffix else Path(canonical)
    return path


def _absolute_without_resolution(path: Path) -> Path:
    return _trusted_macos_prefix(Path(os.path.abspath(os.fspath(path))))


def _directory_identity(info: os.stat_result) -> tuple[int, int]:
    return info.st_dev, info.st_ino


def _secure_existing_directory(path: Path) -> tuple[Path, tuple[int, int]]:
    absolute = _absolute_without_resolution(path)
    current = Path(absolute.anchor)
    parts = absolute.parts[1:] if absolute.anchor else absolute.parts
    try:
        root_info = os.lstat(current)
        if _is_link_or_reparse(root_info) or not stat.S_ISDIR(root_info.st_mode):
            raise UnsafePathError("output path root is not a trusted directory")
        info = root_info
        for part in parts:
            current = current / part
            info = os.lstat(current)
            if _is_link_or_reparse(info):
                raise UnsafePathError("output path cannot contain a symbolic-link or reparse ancestor")
            if not stat.S_ISDIR(info.st_mode):
                raise UnsafePathError("output parent must be an existing directory")
    except UnsafePathError:
        raise
    except OSError as exc:
        raise UnsafePathError(f"output parent must already exist and be readable: {exc}") from exc
    return absolute, _directory_identity(info)


def _open_secure_parent(parent: Path) -> tuple[Path, int | None, tuple[int, int]]:
    secure_parent, identity = _secure_existing_directory(parent)
    supports_dir_fd = os.open in getattr(os, "supports_dir_fd", set())
    if os.name == "nt" or not supports_dir_fd:
        return secure_parent, None, identity
    flags = os.O_RDONLY
    flags |= getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(secure_parent, flags)
        opened_identity = _directory_identity(os.fstat(descriptor))
    except OSError as exc:
        raise UnsafePathError(f"cannot lock the output parent directory: {exc}") from exc
    if opened_identity != identity:
        os.close(descriptor)
        raise UnsafePathError("output parent changed before it could be locked")
    return secure_parent, descriptor, identity


def _parent_still_bound(parent: Path, descriptor: int | None,
                        identity: tuple[int, int]) -> bool:
    try:
        path_info = os.lstat(parent)
        if _is_link_or_reparse(path_info) or _directory_identity(path_info) != identity:
            return False
        return descriptor is None or _directory_identity(os.fstat(descriptor)) == identity
    except OSError:
        return False


def _lexists(path: Path) -> bool:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise UnsafePathError(f"cannot inspect output target: {exc}") from exc
    return True


def explicit_regular_file(raw: str | Path) -> Path:
    path = Path(raw).expanduser()
    if ".." in path.parts:
        raise UnsafePathError("parent-directory traversal is not accepted in v0.1")
    if path.is_symlink():
        raise UnsafePathError("symbolic-link inputs are not accepted in v0.1")
    try:
        resolved = path.resolve(strict=True)
        info = resolved.stat()
    except OSError as exc:
        raise UnsafePathError(f"cannot open the explicit input: {exc}") from exc
    if not stat.S_ISREG(info.st_mode):
        raise UnsafePathError("input must be a regular file")
    if info.st_nlink > 1:
        raise UnsafePathError("hard-linked inputs are not accepted in v0.1")
    return resolved


def private_output_path(raw: str | Path) -> Path:
    path = Path(raw).expanduser()
    if not path.name.endswith(".private.json"):
        raise UnsafePathError("private evidence output must end with .private.json")
    return _new_output_path(path)


def share_output_path(raw: str | Path, suffixes: tuple[str, ...] = (".json", ".md")) -> Path:
    path = Path(raw).expanduser()
    if not any(path.name.endswith(suffix) for suffix in suffixes):
        raise UnsafePathError(f"output must end with one of: {', '.join(suffixes)}")
    return _new_output_path(path)


def new_output_directory(raw: str | Path) -> Path:
    path = Path(raw).expanduser()
    if ".." in path.parts:
        raise UnsafePathError("parent-directory traversal is not accepted in output paths")
    if not path.name or path.name in (".", ".."):
        raise UnsafePathError("output directory needs an explicit final name")
    parent, parent_fd, identity = _open_secure_parent(path.parent)
    target = parent / path.name
    created = False
    try:
        if _lexists(target):
            raise UnsafePathError("refusing to replace an existing output directory")
        if parent_fd is not None and os.mkdir in getattr(os, "supports_dir_fd", set()):
            os.mkdir(path.name, mode=0o700, dir_fd=parent_fd)
        else:
            os.mkdir(target, mode=0o700)
        created = True
        if not _parent_still_bound(parent, parent_fd, identity):
            raise UnsafePathError("output parent changed while creating the directory")
        info = (os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
                if parent_fd is not None and os.stat in getattr(os, "supports_dir_fd", set())
                else os.lstat(target))
        if _is_link_or_reparse(info) or not stat.S_ISDIR(info.st_mode):
            raise UnsafePathError("created output is not a regular directory")
    except UnsafePathError:
        if created:
            try:
                if parent_fd is not None and os.rmdir in getattr(os, "supports_dir_fd", set()):
                    os.rmdir(path.name, dir_fd=parent_fd)
                else:
                    os.rmdir(target)
            except OSError:
                pass
        raise
    except OSError as exc:
        raise UnsafePathError(f"cannot create output directory: {exc}") from exc
    finally:
        if parent_fd is not None:
            os.close(parent_fd)
    return target


def _new_output_path(path: Path) -> Path:
    if ".." in path.parts:
        raise UnsafePathError("parent-directory traversal is not accepted in output paths")
    if not path.name or path.name in (".", ".."):
        raise UnsafePathError("output needs an explicit final name")
    parent, _ = _secure_existing_directory(path.parent)
    target = parent / path.name
    if _lexists(target):
        raise UnsafePathError("refusing to overwrite an existing output")
    return target


def write_new_text(path: Path, text: str, *, private: bool) -> None:
    path = Path(path)
    if ".." in path.parts:
        raise UnsafePathError("parent-directory traversal is not accepted in output paths")
    parent, parent_fd, identity = _open_secure_parent(path.parent)
    target = parent / path.name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    mode = 0o600 if private else 0o644
    fd: int | None = None
    created = False
    try:
        if parent_fd is not None:
            fd = os.open(path.name, flags, mode, dir_fd=parent_fd)
        else:
            fd = os.open(target, flags, mode)
        created = True
    except OSError as exc:
        if parent_fd is not None:
            os.close(parent_fd)
        raise UnsafePathError(f"cannot create output without overwriting: {exc}") from exc
    try:
        assert fd is not None
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            fd = None
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if not _parent_still_bound(parent, parent_fd, identity):
            raise UnsafePathError("output parent changed while the file was being written")
    except Exception:
        if fd is not None:
            os.close(fd)
        try:
            if created and parent_fd is not None and os.unlink in getattr(os, "supports_dir_fd", set()):
                os.unlink(path.name, dir_fd=parent_fd)
            elif created:
                os.unlink(target)
        except OSError:
            pass
        raise
    finally:
        if parent_fd is not None:
            os.close(parent_fd)


def write_new_json(path: Path, value: Any, *, private: bool) -> None:
    write_new_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n", private=private)


def read_json_file(raw: str | Path, expected_kind: str | None = None) -> dict[str, Any]:
    path = explicit_regular_file(raw)
    before = path.stat()
    if before.st_size > MAX_JSON_INPUT_BYTES:
        raise SchemaError("JSON input exceeds the 128 MiB limit")
    try:
        text = path.read_text(encoding="utf-8")
        after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_ino, after.st_size, after.st_mtime_ns
        ):
            raise SchemaError("JSON input changed while it was being read")
        value = json.loads(text)
    except (OSError, ValueError) as exc:
        raise SchemaError(f"cannot read JSON input: {exc}") from exc
    if not isinstance(value, dict):
        raise SchemaError("JSON input must be an object")
    if value.get("schema_version") != "1.0":
        raise SchemaError("unsupported or missing schema_version")
    if expected_kind and value.get("kind") != expected_kind:
        raise SchemaError(f"expected kind={expected_kind}, got {value.get('kind')!r}")
    return value
