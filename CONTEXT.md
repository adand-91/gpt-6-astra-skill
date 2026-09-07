# Project context

Short pickup index; private release evidence stays outside the repository.

## Current checkpoint

- Preparing `v0.2.0-beta.1` (`0.2.0b1`) from the published Alpha 3 baseline.
- This release adds installed audit/daily/weekly review scaffolds and local time-window handling.
- The frozen Beta 1 input passed all three archive checksums. Only its bounded code/tests were
  reused; obsolete publication records, AppleDouble metadata, and later features were excluded.
- Fresh source and extracted-sdist suites each passed 138 tests. Both clean installs passed all
  three modes, private permissions, no-overwrite, invalid-input, and deterministic Demo checks.
- Exact-commit public CI and publication/download verification remain pending.
- Stable v0.1.1 and all prior immutable releases remain intact; cumulative Jarvis work is separate.

## Pickup files

- Scope and usage: `docs/release-notes/v0.2.0-beta.1.md` and `README.md`.
- Gates and history: `docs/RELEASE_CHECKLIST.md`; current technical state: `HANDOFF.md`.

## Next action

Push the exact Beta 1 candidate, verify public CI, publish a non-latest prerelease, then independently
re-download and validate its assets. These release actions are explicitly authorised for Beta 1.

## Safety boundary

Do not publish later candidates, move old tags, replace old assets, promote, rename, submit a
plugin/application, or change the cumulative development worktree's program files.
