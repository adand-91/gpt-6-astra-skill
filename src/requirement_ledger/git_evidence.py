"""Read-only Git snapshot collection.  Remote URLs are never read or emitted."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any

from .errors import InputChangedError, UnsafePathError


def _trusted_git(root: Path) -> Path:
    """Resolve Git from OS installation locations, never the project or a relative PATH."""
    candidates: list[Path] = []
    if os.name == "nt":
        for variable in ("ProgramFiles", "ProgramFiles(x86)"):
            base = os.environ.get(variable)
            if base:
                candidates.extend((Path(base) / "Git" / "cmd" / "git.exe",
                                   Path(base) / "Git" / "bin" / "git.exe"))
    else:
        candidates.extend(Path(value) for value in (
            "/usr/bin/git", "/usr/local/bin/git", "/opt/homebrew/bin/git", "/opt/local/bin/git"
        ))
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            continue
        if not resolved.is_file() or not os.access(resolved, os.X_OK):
            continue
        try:
            resolved.relative_to(root)
        except ValueError:
            return resolved
    raise UnsafePathError("cannot locate Git in a trusted OS installation directory")


def _clean_git_env(git_executable: Path) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "PAGER": "cat",
    })
    if os.name == "nt":
        env["PATH"] = str(git_executable.parent)
    else:
        env["PATH"] = os.pathsep.join((str(git_executable.parent), "/usr/bin", "/bin"))
    return env


def _git(root: Path, git_executable: Path, *argv: str) -> str:
    env = _clean_git_env(git_executable)
    command = [
        str(git_executable), "-c", "core.fsmonitor=false",
        "-c", f"core.hooksPath={os.devnull}",
        "-C", str(root), *argv,
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UnsafePathError(f"read-only Git probe failed: {exc}") from exc
    if result.returncode != 0:
        raise UnsafePathError("explicit repository is not a readable non-bare Git worktree")
    return result.stdout.rstrip("\n")


def bind_repo(raw: str | Path) -> tuple[Path, dict[str, Any]]:
    supplied = Path(raw).expanduser()
    if ".." in supplied.parts:
        raise UnsafePathError("parent-directory traversal is not accepted for a repository")
    if supplied.is_symlink():
        raise UnsafePathError("repository path cannot be a symbolic link")
    try:
        root = supplied.resolve(strict=True)
    except OSError as exc:
        raise UnsafePathError(f"cannot resolve repository: {exc}") from exc
    if not root.is_dir():
        raise UnsafePathError("repository must be a directory")
    git_executable = _trusted_git(root)
    top = Path(_git(root, git_executable, "rev-parse", "--show-toplevel")).resolve(strict=True)
    if top != root:
        raise UnsafePathError("bind the repository root explicitly, not a nested directory")
    if _git(root, git_executable, "rev-parse", "--is-bare-repository") != "false":
        raise UnsafePathError("bare repositories are not supported")

    head_before = _git(root, git_executable, "rev-parse", "--verify", "HEAD")
    status_before = _git(root, git_executable, "status", "--porcelain=v1", "--untracked-files=normal")
    tracked = _git(root, git_executable, "ls-files", "-z").count("\0")
    head_after = _git(root, git_executable, "rev-parse", "--verify", "HEAD")
    status_after = _git(root, git_executable, "status", "--porcelain=v1", "--untracked-files=normal")
    if head_before != head_after or status_before != status_after:
        raise InputChangedError("Git HEAD or worktree status changed during the read-only snapshot")
    entries = [line for line in status_after.splitlines() if line]
    digest = hashlib.sha256(status_after.encode("utf-8")).hexdigest()
    snapshot = {
        "head": head_after,
        "status_digest": digest,
        "dirty_entries": len(entries),
        "tracked_files": tracked,
        "linked_worktree": (root / ".git").is_file(),
        "remote_urls_read": False,
        "read_only": True,
        "git_executable_trusted": True,
        "redirecting_git_environment_removed": True,
    }
    return root, snapshot
