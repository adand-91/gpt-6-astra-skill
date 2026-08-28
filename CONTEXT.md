# Project context

This is the short pickup index for Requirement Ledger. Historical conversations and private
evidence do not belong in this repository.

## Current checkpoint

- Stage: public `main` contains the `v0.1.0` release candidate; the tag and GitHub Release remain
  blocked until the final cross-platform CI run is green.
- Product: explicit Git project + explicit transcript/test evidence → private evidence →
  conservative attribution → quote-free report and not-applied repair plan → external
  same-oracle validation.
- Safety: the CLI does not discover home sessions, run project code, install dependencies,
  access a network, edit the worktree, commit, push, or perform GitHub/account actions.
- Verification: 96 local tests, compile, translation, targeted security regressions, wheel/sdist
  build and clean installs, deterministic demo, explicit-input smoke, Git no-change check, and
  privacy canary have passed.
- Publication: release-candidate commits are pushed through `6c0078c`; no `v0.1.0` tag or GitHub
  Release exists yet. The next commit closes the Windows Python 3.13 test-log stat mismatch.

## Pickup files

- Product and permissions: `V0.1_CONTRACT.md`
- Architecture and threat model: `docs/ARCHITECTURE.md`, `docs/THREAT_MODEL.md`
- Remaining work: `docs/PROJECT_GAPS.md`
- Maintenance and batches: `MAINTENANCE.md`
- Release gate and notes: `docs/RELEASE_CHECKLIST.md`, `docs/releases/v0.1.0.md`
- Rolling technical handoff: `HANDOFF.md`

## Next action

Commit and push the test-log stability fix, then run the public cross-platform CI. Only a green
run may be tagged and published as GitHub Release `v0.1.0`.
