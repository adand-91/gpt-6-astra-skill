# Project context

Short pickup index; private evidence stays outside the repository.

## Current checkpoint

- `v0.2.0-alpha.3` (`0.2.0a3`) is publicly available as a non-latest GitHub prerelease. Tagged
  commit: `dfa04a0d21ff0aca5c97d87b40546c58fe39d199`; annotated tag object:
  `af32da5b81c12317177042875ffd08a8f03b816c`.
- Alpha 3 adds bounded normalization for supported modern Codex rollout records: ordered
  completed-item snapshots, turn terminals, structured exclusions, exact record conservation,
  canonical tuple identity, and a 1,000,000-record work cap.
- The reconstructed source passed 132 source tests, 19 focused normalization/envelope tests,
  translation sync, compile, build, clean-install, privacy, and deterministic-output checks. The
  exact final commit must pass public Linux/macOS/Windows CI before tagging.
- The maintainer's cumulative post-Alpha dirty worktree remains untouched. Beta, RC, stable,
  Jarvis, and later usability changes are not part of Alpha 3.
- The tagged commit passed final public CI runs `33708129443` and `33708228485`: all 12 Python
  3.10–3.13 Linux/macOS/Windows jobs and the built-artefact/security smoke succeeded. All three
  public assets were re-downloaded, hash-verified, and exercised through clean installs.

## Pickup files

- Changes: `CHANGELOG.md`; release notes: `docs/release-notes/v0.2.0-alpha.3.md`
- Release: <https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.3>
- Modern normalization: `src/requirement_ledger/transcript.py` and
  `src/requirement_ledger/codex_input.py`
- Regressions: `tests/test_codex_modern_normalization.py` and
  `tests/test_codex_input_envelope.py`
- Publication gate: `docs/RELEASE_CHECKLIST.md`; technical state: `HANDOFF.md`

## Next action

Stop at the completed Alpha 3 publication and report its evidence and current GitHub metrics.
Later queued versions continue at the normal release cadence; the larger Jarvis/usability changes
remain held for `v1.0.0-rc.1`.

## Safety boundary

Do not move existing tags or replace published assets. Do not include later queued versions,
promote, rename the repository, submit a plugin, apply to a programme, create Issues/PRs, send
external messages, or alter the maintainer's cumulative development worktree.
