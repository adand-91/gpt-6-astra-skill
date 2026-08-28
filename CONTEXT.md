# Project context

This is the short pickup index for Requirement Ledger. Historical conversations and private
evidence do not belong in this repository.

## Current checkpoint

- Stage: local `v0.1.0` release candidate; public repository still points to the earlier
  retrospective-only commit until release gates and publication authority are satisfied.
- Product: explicit Git project + explicit transcript/test evidence → private evidence →
  conservative attribution → quote-free report and not-applied repair plan → external
  same-oracle validation.
- Safety: the CLI does not discover home sessions, run project code, install dependencies,
  access a network, edit the worktree, commit, push, or perform GitHub/account actions.
- Verification: 94 local tests, compile, translation, targeted security regressions, wheel/sdist
  build and clean installs, deterministic demo, explicit-input smoke, Git no-change check, and
  privacy canary have passed.
- Publication: no v0.1 commit, tag, push, or GitHub Release has occurred yet.

## Pickup files

- Product and permissions: `V0.1_CONTRACT.md`
- Architecture and threat model: `docs/ARCHITECTURE.md`, `docs/THREAT_MODEL.md`
- Remaining work: `docs/PROJECT_GAPS.md`
- Maintenance and batches: `MAINTENANCE.md`
- Release gate and notes: `docs/RELEASE_CHECKLIST.md`, `docs/releases/v0.1.0.md`
- Rolling technical handoff: `HANDOFF.md`

## Next action

Refresh `HANDOFF.md`, make one coherent release-candidate commit, push it, and wait for the public
cross-platform CI. Only a green run may be tagged and published as GitHub Release `v0.1.0`.
