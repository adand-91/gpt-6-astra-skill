# Project context

Short pickup index; private evidence stays outside the repository.

## Current checkpoint

- `v0.2.0-alpha.2` (`0.2.0a2`) is publicly available as a non-latest GitHub prerelease. Tagged
  commit: `fb49947627516bca463094becde16a63d047e2d6`; annotated tag object:
  `00fb12747e93f9c48f24c434b5d329fbdad57bf4`. The maintainer's cumulative post-Alpha dirty
  worktree remains untouched.
- Alpha 2 adds an explicit bounded `codex-scan` input envelope: task/target digests, a half-open
  time window, record accounting, and honest partial/unknown coverage. It does not retain raw
  target text or local paths.
- The restored source passes 122 Python 3.12 tests, translation sync, and `git diff --check`.
  The sealed wheel and sdist match their recorded SHA-256 hashes.
- Tagged commit passed public CI runs `33468720368` and `33468928114` across Python 3.10–3.13 on
  Linux/macOS/Windows plus built-artefact/security smoke. All three public assets were re-downloaded,
  hash-verified, and exercised through clean wheel/sdist installs and the Alpha 2 command chain.

## Pickup files

- Release: <https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.2>
- Changes: `CHANGELOG.md`; release notes: `docs/release-notes/v0.2.0-alpha.2.md`
- Input implementation: `src/requirement_ledger/codex_input.py`; CLI: `src/requirement_ledger/cli.py`
- Regression: `tests/test_codex_input_envelope.py`; publication gate: `docs/RELEASE_CHECKLIST.md`
- Daily train: `UPDATE_MAP.md`; technical state: `HANDOFF.md`

## Next action

Stop at the completed Alpha 2 publication and report its evidence. Alpha 3 is the next mapped
candidate, but implementation or publication requires a separate user instruction.

## Safety boundary

Do not move the Alpha 2 tag or replace its assets. Later versions, Issues, PRs, promotion,
repository rename, plugin submission, programme application, unrelated-history reads, and
destructive changes to the maintainer worktree remain out of scope.
