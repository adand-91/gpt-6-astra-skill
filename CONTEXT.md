# Project context

Short pickup index; private evidence stays outside the repository.

## Current checkpoint

- `v0.2.0-alpha.3` (`0.2.0a3`) is being reconstructed in an isolated release worktree from
  `origin/main`, preserving the immutable Alpha 2 publication record.
- Alpha 3 adds bounded normalization for supported modern Codex rollout records: ordered
  completed-item snapshots, turn terminals, structured exclusions, exact record conservation,
  canonical tuple identity, and a 1,000,000-record work cap.
- The reconstructed source passed 132 source tests, 19 focused normalization/envelope tests,
  translation sync, compile, build, clean-install, privacy, and deterministic-output checks. The
  exact final commit must pass public Linux/macOS/Windows CI before tagging.
- The maintainer's cumulative post-Alpha dirty worktree remains untouched. Beta, RC, stable,
  Jarvis, and later usability changes are not part of Alpha 3.

## Pickup files

- Changes: `CHANGELOG.md`; release notes: `docs/release-notes/v0.2.0-alpha.3.md`
- Modern normalization: `src/requirement_ledger/transcript.py` and
  `src/requirement_ledger/codex_input.py`
- Regressions: `tests/test_codex_modern_normalization.py` and
  `tests/test_codex_input_envelope.py`
- Publication gate: `docs/RELEASE_CHECKLIST.md`; technical state: `HANDOFF.md`

## Next action

Commit and push the locally verified source, require public cross-platform CI, then finalize the
release-facing status and repeat CI if the commit changes. Only then create the annotated tag and
non-latest GitHub prerelease with freshly rebuilt assets.

## Safety boundary

Do not move existing tags or replace published assets. Do not include later queued versions,
promote, rename the repository, submit a plugin, apply to a programme, create Issues/PRs, send
external messages, or alter the maintainer's cumulative development worktree.
