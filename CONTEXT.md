# Project context

This is the short pickup index for Requirement Ledger. Historical conversations and private
evidence do not belong in this repository.

## Current checkpoint

- Stage: public `main` contains the `v0.1.0` release candidate and the full public release gate is
  green; the tag and GitHub Release are the remaining publication actions.
- Product: explicit Git project + explicit transcript/test evidence → private evidence →
  conservative attribution → quote-free report and not-applied repair plan → external
  same-oracle validation.
- Safety: the CLI does not discover home sessions, run project code, install dependencies,
  access a network, edit the worktree, commit, push, or perform GitHub/account actions.
- Verification: 96 local tests, compile, translation, targeted security regressions, wheel/sdist
  build and clean installs, deterministic demo, explicit-input smoke, Git no-change check, and
  privacy canary have passed.
- Publication: release-candidate commits are pushed through `97b22f8`; CI run `33154009605` is
  fully green. No `v0.1.0` tag or GitHub Release exists yet.

## Pickup files

- Product and permissions: `V0.1_CONTRACT.md`
- Architecture and threat model: `docs/ARCHITECTURE.md`, `docs/THREAT_MODEL.md`
- Remaining work: `docs/PROJECT_GAPS.md`
- Maintenance and batches: `MAINTENANCE.md`
- Release gate and notes: `docs/RELEASE_CHECKLIST.md`, `docs/releases/v0.1.0.md`
- Rolling technical handoff: `HANDOFF.md`

## Next action

Record the green release gate, rebuild wheel/sdist from the final clean commit, create tag
`v0.1.0`, publish the GitHub Release, and verify the public install and demo path.
