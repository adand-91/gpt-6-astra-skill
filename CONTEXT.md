# Project context

Short pickup index; private evidence stays outside the repository.

## Current checkpoint

- `v0.2.0-alpha.1` (`0.2.0a1`) is publicly available as a non-latest GitHub prerelease.
  Tagged commit: `243b01ac5be88825ec4a1f4f9c5cec3b2841a90e`; annotated tag object:
  `856f4d0fd198a74825f134289af3b0475042ec85`. Stable `v0.1.1` remains latest.
- CI run `33291029715` passed Python 3.10–3.13 on Linux/macOS/Windows and the
  built-artefact/security smoke. All three public assets were re-downloaded, hash-verified, clean
  installed, and exercised through Demo plus audit create/check.
- Alpha 1 ships a private, no-overwrite named-target `review-init --mode audit` scaffold, strict
  `review-check`, bilingual notes, and an update map. It does not retrieve Codex history or
  initialise daily/weekly reviews.
- The update map targets one substantive candidate per successful release day:
  `alpha.1 → alpha.2 → alpha.3 → beta.1 → beta.2 → beta.3 → rc.1 → rc.2 → rc.3 → v0.2.0`.
  A failed gate shifts the train; no empty version is published.
- This isolated worktree is the Alpha publication source. The maintainer's dirty post-Alpha
  worktree remains untouched.

## Pickup files

- Release: <https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.1>
- Changes: `CHANGELOG.md`; release notes: `docs/release-notes/v0.2.0-alpha.1.md`
- Daily train: `UPDATE_MAP.md`; product path: `ROADMAP.md`
- Publication evidence: `docs/RELEASE_CHECKLIST.md`; technical state: `HANDOFF.md`

## Next action

Land this factual publication/map record on `main` and verify its CI. The next product candidate
is Alpha 2: one explicit bounded input envelope for a user-selected Codex task/export.

## Safety boundary

Do not move the Alpha tag or replace its assets. Candidate dates do not bypass release gates.
Issues, PRs, promotion, programme applications, schedules, unrelated-history reads, and destructive
changes to the maintainer worktree remain outside this batch.
