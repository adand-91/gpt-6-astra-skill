"""Small fail-closed file helpers."""

from __future__ import annotations

import json
import os
import stat
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Iterator

from .errors import InputChangedError, InputLimitError, SchemaError, UnsafePathError

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


def _file_snapshot(info: os.stat_result) -> tuple[int, int, int, int, int]:
    """Identity plus mutation-sensitive metadata for one open regular file."""
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        getattr(info, "st_mtime_ns", int(info.st_mtime * 1_000_000_000)),
        getattr(info, "st_ctime_ns", int(info.st_ctime * 1_000_000_000)),
    )


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
    if os.name == "nt":
        return secure_parent, None, identity
    if not supports_dir_fd:
        raise UnsafePathError("secure relative output creation is unavailable on this platform")
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


@dataclass(frozen=True)
class ScopedInput:
    """One open input whose lexical scope and component identities are bound in memory."""

    path: Path
    scope_root: Path
    handle: BinaryIO
    opened_stat: os.stat_result


def _strict_existing_chain(
    raw: str | Path,
    *,
    final_kind: str,
) -> tuple[Path, tuple[tuple[int, int], ...], os.stat_result]:
    path = Path(raw).expanduser()
    if ".." in path.parts:
        raise UnsafePathError("scoped input paths cannot contain parent-directory traversal")
    absolute = _absolute_without_resolution(path)
    current = Path(absolute.anchor)
    parts = absolute.parts[1:] if absolute.anchor else absolute.parts
    identities: list[tuple[int, int]] = []
    try:
        info = os.lstat(current)
        if _is_link_or_reparse(info) or not stat.S_ISDIR(info.st_mode):
            raise UnsafePathError("scoped input anchor must be a trusted directory")
        identities.append(_directory_identity(info))
        for index, part in enumerate(parts):
            current = current / part
            info = os.lstat(current)
            if _is_link_or_reparse(info):
                raise UnsafePathError(
                    "scoped input paths cannot contain symbolic-link or reparse components"
                )
            is_final = index == len(parts) - 1
            if not is_final and not stat.S_ISDIR(info.st_mode):
                raise UnsafePathError("scoped input ancestors must be directories")
            identities.append(_directory_identity(info))
    except (UnsafePathError, InputChangedError):
        raise
    except OSError as exc:
        raise UnsafePathError("scoped input path must already exist and be readable") from exc

    if final_kind == "directory" and not stat.S_ISDIR(info.st_mode):
        raise UnsafePathError("scope root must be an existing directory")
    if final_kind == "file":
        if not stat.S_ISREG(info.st_mode):
            raise UnsafePathError("scoped input must be a regular file")
        if info.st_nlink != 1:
            raise UnsafePathError("scoped input must have exactly one hard link")
    return absolute, tuple(identities), info


def _same_chain(
    raw: Path,
    expected: tuple[tuple[int, int], ...],
    *,
    final_kind: str,
) -> bool:
    try:
        _, current, _ = _strict_existing_chain(raw, final_kind=final_kind)
    except UnsafePathError:
        return False
    return current == expected


def _forbidden_scope_root(path: Path) -> bool:
    if path == Path(path.anchor):
        return True
    candidates: list[Path] = []
    try:
        candidates.append(Path.home())
    except (OSError, RuntimeError):
        pass
    if os.name == "posix":
        try:
            import pwd

            candidates.append(Path(pwd.getpwuid(os.getuid()).pw_dir))
        except (ImportError, KeyError, OSError):
            pass
    elif os.name == "nt":
        try:
            from ._win32safe import profile_directory

            candidates.append(profile_directory())
        except OSError as exc:
            raise UnsafePathError(
                "cannot establish the current Windows Profile directory"
            ) from exc
    for candidate in candidates:
        try:
            if os.path.samefile(path, candidate):
                return True
        except OSError:
            continue
    return False


def _open_scoped_descriptor(
    scope_root: Path,
    relative: Path,
    expected_file: os.stat_result,
) -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    supports_dir_fd = os.open in getattr(os, "supports_dir_fd", set())
    if os.name == "nt" or not supports_dir_fd:
        descriptor = os.open(scope_root / relative, flags)
        if not os.path.samestat(expected_file, os.fstat(descriptor)):
            os.close(descriptor)
            raise InputChangedError("scoped input changed before it could be bound")
        return descriptor

    directory_fd: int | None = None
    try:
        directory_fd = os.open(scope_root, directory_flags)
        for part in relative.parts[:-1]:
            next_fd = os.open(part, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        descriptor = os.open(relative.name, flags, dir_fd=directory_fd)
    except OSError as exc:
        raise UnsafePathError("cannot securely open the scoped input") from exc
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
    if not os.path.samestat(expected_file, os.fstat(descriptor)):
        os.close(descriptor)
        raise InputChangedError("scoped input changed before it could be bound")
    return descriptor


@contextmanager
def open_scoped_regular_input(
    raw: str | Path,
    scope_root: str | Path,
) -> Iterator[ScopedInput]:
    """Open one explicit file without following a link/reparse boundary.

    The caller chooses a non-home, non-filesystem-root directory.  No discovery or recursive
    enumeration occurs.  On POSIX the relative path is opened component-by-component with
    ``dir_fd`` and ``O_NOFOLLOW``; other platforms use repeated reparse and identity checks.
    macOS's root-owned ``/var``, ``/tmp``, and ``/etc`` compatibility aliases are first mapped to
    their fixed ``/private`` targets by the same narrow allowlist used for safe outputs.
    """

    root, root_chain, _ = _strict_existing_chain(scope_root, final_kind="directory")
    if _forbidden_scope_root(root):
        raise UnsafePathError("scope root cannot be a filesystem root or the user home directory")
    source, source_chain, source_info = _strict_existing_chain(raw, final_kind="file")
    try:
        relative = source.relative_to(root)
    except ValueError as exc:
        raise UnsafePathError("scoped input must stay inside the explicit scope root") from exc
    if not relative.parts:
        raise UnsafePathError("scoped input needs an explicit file below the scope root")

    descriptor = _open_scoped_descriptor(root, relative, source_info)
    handle = os.fdopen(descriptor, "rb")
    opened = os.fstat(handle.fileno())
    if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
            or not os.path.samestat(source_info, opened)):
        handle.close()
        raise InputChangedError("scoped input changed before it could be bound")
    try:
        yield ScopedInput(path=source, scope_root=root, handle=handle, opened_stat=opened)
    except BaseException:
        raise
    else:
        if (not _same_chain(root, root_chain, final_kind="directory")
                or not _same_chain(source, source_chain, final_kind="file")):
            raise InputChangedError("scoped input boundary changed while it was being read")
        try:
            path_after = os.lstat(source)
            final_fd = os.fstat(handle.fileno())
        except OSError as exc:
            raise InputChangedError("scoped input changed while it was being read") from exc
        if (_file_snapshot(opened) != _file_snapshot(path_after)
                or _file_snapshot(opened) != _file_snapshot(final_fd)):
            raise InputChangedError("scoped input changed while it was being read")
    finally:
        handle.close()


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
    if os.name == "nt":
        try:
            from ._win32safe import create_new_directory

            return create_new_directory(
                parent,
                path.name,
                expected_parent_identity=identity,
            )
        except (OSError, TypeError, ValueError) as exc:
            raise UnsafePathError(
                f"cannot create a safe Windows output directory: {exc}"
            ) from exc
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
    if os.name == "nt":
        try:
            from ._win32safe import create_new_file

            create_new_file(
                parent,
                path.name,
                text.encode("utf-8"),
                mode,
                expected_parent_identity=identity,
            )
            return
        except (OSError, TypeError, ValueError, UnicodeError) as exc:
            raise UnsafePathError(f"cannot create a safe Windows output: {exc}") from exc
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


@contextmanager
def open_scoped_json_object(
    raw: str | Path,
    scope_root: str | Path,
    *,
    max_bytes: int = MAX_JSON_INPUT_BYTES,
) -> Iterator[dict[str, Any]]:
    """Yield one bounded JSON object while retaining its descriptor-bound input lock."""
    if type(max_bytes) is not int or max_bytes < 1 or max_bytes > MAX_JSON_INPUT_BYTES:
        raise InputLimitError("JSON input limit must be between 1 byte and 128 MiB")
    with open_scoped_regular_input(raw, scope_root) as source:
        if source.opened_stat.st_size > max_bytes:
            raise InputLimitError("JSON input exceeds its explicit byte limit")
        payload = source.handle.read(max_bytes + 1)
        if len(payload) > max_bytes:
            raise InputLimitError("JSON input exceeded its explicit byte limit while reading")
        try:
            value = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SchemaError(f"cannot read JSON input: {exc}") from exc
        if not isinstance(value, dict):
            raise SchemaError("JSON input must be an object")
        yield value


def read_scoped_json_object(
    raw: str | Path,
    scope_root: str | Path,
    *,
    max_bytes: int = MAX_JSON_INPUT_BYTES,
) -> dict[str, Any]:
    """Read and close one descriptor-bound, bounded JSON object."""
    with open_scoped_json_object(raw, scope_root, max_bytes=max_bytes) as value:
        return value


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
