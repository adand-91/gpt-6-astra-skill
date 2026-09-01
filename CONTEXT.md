# Project context

Short pickup index; private evidence stays outside the repository.

## Current checkpoint

- `v0.2.0-alpha.2` (`0.2.0a2`) has been restored from the sealed final-candidate snapshot into an
  isolated release worktree based on `origin/main`. The maintainer's cumulative post-Alpha dirty
  worktree remains untouched.
- Alpha 2 adds an explicit bounded `codex-scan` input envelope: task/target digests, a half-open
  time window, record accounting, and honest partial/unknown coverage. It does not retain raw
  target text or local paths.
- The restored source passes 122 Python 3.12 tests, translation sync, and `git diff --check`.
  The sealed wheel and sdist match their recorded SHA-256 hashes.
- Public CI, the annotated tag, GitHub prerelease, public asset download, and clean-install checks
  are still pending. No later queued version is included in this boundary.

## Pickup files

- Changes: `CHANGELOG.md`; candidate notes: `docs/release-notes/v0.2.0-alpha.2.md`
- Input implementation: `src/requirement_ledger/codex_input.py`; CLI: `src/requirement_ledger/cli.py`
- Regression: `tests/test_codex_input_envelope.py`; publication gate: `docs/RELEASE_CHECKLIST.md`
- Daily train: `UPDATE_MAP.md`; technical state: `HANDOFF.md`

## Next action

Commit and push this exact Alpha 2 boundary to `main`, then wait for public CI. A failed gate stops
tag and Release creation; a green gate permits only the Alpha 2 annotated tag, prerelease, assets,
and independent download verification.

## Safety boundary

This batch authorises only `v0.2.0-alpha.2` commit, push, tag, prerelease, assets, and verification.
Later versions, Issues, PRs, promotion, repository rename, plugin submission, programme application,
unrelated-history reads, and destructive changes to the maintainer worktree remain out of scope.
