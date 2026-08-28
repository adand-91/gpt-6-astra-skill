# Project context

This is the short pickup index for Requirement Ledger. Historical conversations and private
evidence do not belong in this repository.

## Current checkpoint

- Stage: `v0.1.1` is an approved release candidate; the implementation commit passed public CI
  run `33158962532`, and the final evidence commit must pass before tagging.
- Brand: Requirement Ledger AI — an AI project and Skill feedback loop for Codex, Claude Code,
  and any Git project. The repository slug and CLI remain `requirement-ledger`.
- Product: explicit Git project + explicit transcript/test evidence → private evidence →
  conservative attribution → quote-free report and not-applied repair plan → external
  same-oracle validation.
- Safety: the CLI does not discover home sessions, run project code, install dependencies,
  access a network, edit the worktree, commit, push, or perform GitHub/account actions.
- Verification: 97 local tests, compile, translation, wheel/sdist build and clean installs,
  deterministic Demo, package-content checks, and the synthetic Skill case have passed. The case
  produced oracle exits `1 -> 0`, `improved`, `unknown` attribution, and no raw failure in its
  report.
- Publication: `v0.1.0` remains the current public release. `v0.1.1` has not yet been tagged or
  released; the final evidence-only commit and its CI are the remaining pre-tag gates.

## Pickup files

- Product and permissions: `V0.1_CONTRACT.md`
- Architecture and threat model: `docs/ARCHITECTURE.md`, `docs/THREAT_MODEL.md`
- Remaining work: `docs/PROJECT_GAPS.md`
- Maintenance and batches: `MAINTENANCE.md`; fifteen-day track: `ROADMAP.md`
- Release gate and notes: `docs/RELEASE_CHECKLIST.md`, `docs/releases/v0.1.1.md`
- Synthetic Skill case: `docs/use-cases/improve-an-agent-skill.md`
- Rolling technical handoff: `HANDOFF.md`

## Next action

Push the final evidence update, require all public CI jobs to pass again, then create the tag and
Release from that exact commit. After publication, begin `v0.2.0` report design from explicit
evidence windows; do not add autonomous editing or GitHub actions.
