# Project context

Short pickup index; private evidence stays outside the repository.

## Current checkpoint

- Preparing GitHub prerelease `v0.2.0-alpha.1`; package version is `0.2.0a1`. Public state remains
  `v0.1.1` until the exact release commit passes public CI.
- This isolated worktree starts at `origin/main` and restores only the sealed Alpha source. The
  maintainer's mixed post-Alpha worktree remains untouched.
- Alpha scope is limited to a private, no-overwrite named-target `review-init --mode audit`
  scaffold, strict `review-check`, and supporting bilingual host contracts/templates.
- Daily/weekly CLI initialisation, modern Codex export parsing, candidate carry-over, report-pack
  binding, handoff verification, scheduling, autonomous edits, and Skill-health are not included.
- Bilingual changelog, release notes, ten-day update map, README, roadmap, CI smoke, and release
  checklist now state the shipped boundary and path to stable `v0.2.0`.
- Current source gate: 112 tests, translation sync, and diff check pass. Final build, clean
  installs, privacy/path smokes, public CI, tag, prerelease, and re-download checks remain.

## Pickup files

- Release boundary: `docs/release-notes/v0.2.0-alpha.1.md`
- Ten-day plan: `UPDATE_MAP.md`; longer product path: `ROADMAP.md`
- Product contracts: `V0.1_CONTRACT.md`, `V0.2_HOST_CONTRACT.md`
- Release gate: `docs/RELEASE_CHECKLIST.md`; technical state: `HANDOFF.md`

## Next action

Finalise `HANDOFF.md`, run the complete local release gate, commit and push the exact Alpha source,
wait for public CI, then create annotated tag `v0.2.0-alpha.1` and a non-latest GitHub prerelease.
Re-download every public asset before recording publication evidence.

## Safety boundary

Authority covers the exact Alpha commit, push to `main`, annotated tag, release assets, and GitHub
prerelease. It does not cover Issues, PRs, promotion, programme applications, schedules, unrelated
history reads, other versions, or cleaning/resetting the maintainer's dirty worktree.
