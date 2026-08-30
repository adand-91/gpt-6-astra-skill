# Project context

Short pickup index; private evidence stays outside the repository.

## Current checkpoint

- Preparing `v0.2.0-alpha.1` (`0.2.0a1`). CI commit `a880e9b` passed Unix but failed Windows for
  missing IANA data; no tag/Release exists. The fix adds conditional `tzdata` and an actionable error.
- This isolated worktree contains only sealed Alpha source; the mixed maintainer tree is untouched.
- Alpha scope is limited to a private, no-overwrite named-target `review-init --mode audit`
  scaffold, strict `review-check`, and supporting bilingual host contracts/templates.
- Daily/weekly CLI initialisation, modern Codex export parsing, candidate carry-over, report-pack
  binding, handoff verification, scheduling, autonomous edits, and Skill-health are not included.
- Bilingual notes, update map, roadmap, CI smoke, and release checklist define the v0.2 path.
- Corrected source gate: 113 tests, translation sync, and diff check. Rebuild, clean installs,
  privacy/path smokes, corrected public CI, tag, prerelease, and re-download checks remain.

## Pickup files

- Release boundary: `docs/release-notes/v0.2.0-alpha.1.md`
- Ten-day plan: `UPDATE_MAP.md`; longer product path: `ROADMAP.md`
- Product contracts: `V0.1_CONTRACT.md`, `V0.2_HOST_CONTRACT.md`
- Release gate: `docs/RELEASE_CHECKLIST.md`; technical state: `HANDOFF.md`

## Next action

Repeat all local gates, commit/push the Windows fix, and wait for CI. Only then create annotated tag
`v0.2.0-alpha.1` and a non-latest prerelease; re-download every asset before recording evidence.

## Safety boundary

Authority covers the exact Alpha commit, push to `main`, annotated tag, release assets, and GitHub
prerelease. It does not cover Issues, PRs, promotion, programme applications, schedules, unrelated
history reads, other versions, or cleaning/resetting the maintainer's dirty worktree.
