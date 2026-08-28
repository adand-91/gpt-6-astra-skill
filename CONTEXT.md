# Project context

This is the short pickup index for Requirement Ledger. Historical conversations and private
evidence do not belong in this repository.

## Current checkpoint

- Stage: `v0.1.0` is publicly released; `main` now enters evidence-driven maintenance.
- Product: explicit Git project + explicit transcript/test evidence → private evidence →
  conservative attribution → quote-free report and not-applied repair plan → external
  same-oracle validation.
- Safety: the CLI does not discover home sessions, run project code, install dependencies,
  access a network, edit the worktree, commit, push, or perform GitHub/account actions.
- Verification: 96 local tests, compile, translation, targeted security regressions, wheel/sdist
  build and clean installs, deterministic demo, explicit-input smoke, Git no-change check, and
  privacy canary have passed.
- Publication: annotated tag `v0.1.0` points to `ebda351`; the GitHub Release is public with a
  wheel and sdist. Public re-download hashes, clean wheel install, version, and Demo passed.

## Pickup files

- Product and permissions: `V0.1_CONTRACT.md`
- Architecture and threat model: `docs/ARCHITECTURE.md`, `docs/THREAT_MODEL.md`
- Remaining work: `docs/PROJECT_GAPS.md`
- Maintenance and batches: `MAINTENANCE.md`
- Release gate and notes: `docs/RELEASE_CHECKLIST.md`, `docs/releases/v0.1.0.md`
- Rolling technical handoff: `HANDOFF.md`

## Next action

Watch real usage and Issues. Create a `0.1.x` fix only from reproducible evidence; plan daily or
weekly reporting and structured test adapters as honest `0.2.0` work.
