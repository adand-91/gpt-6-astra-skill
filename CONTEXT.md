# Project context

Short pickup index; private release evidence stays outside the repository.

## Current checkpoint

- `v0.2.0-beta.1` (`0.2.0b1`) is published as a non-latest GitHub prerelease.
- This release adds installed audit/daily/weekly review scaffolds and local time-window handling.
- The frozen Beta 1 input passed all three archive checksums. Only its bounded code/tests were
  reused; obsolete publication records, AppleDouble metadata, and later features were excluded.
- Fresh source and extracted-sdist suites each passed 138 tests. Both clean installs passed all
  three modes, private permissions, no-overwrite, invalid-input, and deterministic Demo checks.
- Exact-commit branch, main and tag CI passed (34080729594 / 34080824950 / 34080827166).
- All three public assets were re-downloaded and matched; both clean installs and three-mode checks passed.
- Stable v0.1.1 and all prior immutable releases remain intact; cumulative Jarvis work is separate.

## Pickup files

- Scope and usage: `docs/release-notes/v0.2.0-beta.1.md` and `README.md`.
- Gates and history: `docs/RELEASE_CHECKLIST.md`; current technical state: `HANDOFF.md`.

## Next action

Report completed Beta 1 publication and the repository metrics, then stop. Later candidates need
a separate release decision.

## Safety boundary

Do not publish later candidates, move old tags, replace old assets, promote, rename, submit a
plugin/application, or change the cumulative development worktree's program files.
