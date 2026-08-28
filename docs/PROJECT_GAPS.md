# Project gap ledger

This ledger records the distance between the original transcript-retrospective Skill and a
mature general project optimiser. It prevents a polished README from hiding missing product
behaviour.

## Closed for v0.1

- Standard `src/` package, semantic version, console entry point, wheel/sdist metadata.
- Explicit repository and input binding; no default home-directory discovery in the new CLI.
- Shared v1 data model for sources, evidence, issues, proposals, and validation.
- Read-only Git snapshot that does not inspect remotes.
- Claude, Codex, and plain-text event normalisation with event-level time filtering.
- Private evidence output, non-overwrite writes, restrictive modes, input mutation checks.
- Automated privacy category detection and a fail-closed share-output gate.
- Conservative four-scope attribution with `unknown` as the default.
- Repair proposals that are mechanically marked `DRAFT — NOT SENT` and `not-applied`.
- External baseline/after result comparison without running untrusted project code.
- Synthetic end-to-end demo, anonymous fixtures, CI matrix, release/community documentation.
- Compatibility retention for the original three scripts and retrospective Skill workflow.

## Open after v0.1 — product

- Semantic grouping of many related corrections into one issue with human confirmation.
- Provider-version compatibility registry and maintained real-format fixtures.
- A structured adapter for JUnit, pytest JSON, TAP, cargo, Go, Maven, npm, and other test logs.
- Clean-room reproduction helpers that can actually confirm `project-local` or `upstream`.
- A user-approved comparison adapter for personal configuration.
- Cross-session evidence linking without exposing low-entropy identifiers.
- A Codex-host integration that passes the private evidence reference without placing raw
  transcript data in prompts unnecessarily.
- Daily improvement reports and weekly ecosystem/maintenance reports.
- Adoption records: installs, repeat users, accepted fixes, before/after outcomes, and
  maintainer response — opt-in and never collected as telemetry by default.
- Internationalisation of generated CLI/report text, not only documentation.
- Windows reparse/junction and case-collision hardening beyond ordinary CI coverage.

## Open after v0.1 — safe modification

- An isolation backend with proof of network and filesystem boundaries on each host OS.
- Object-bound, expiring, one-time approvals tied to repo identity, HEAD/status, exact patch,
  preimages, validation argv, environment, timeout, and file-operation list.
- Patch generation restricted to ordinary text changes with parser-aware preimage validation.
- Isolation-only patch application with byte-for-byte proof the real worktree did not change.
- Frozen oracle execution with CPU, memory, wall-clock, process, file, and output limits.
- Transactional real-worktree apply, failure injection, complete rollback, and audit record.
- Explicit designs for renames, deletes, chmod, binary files, submodules, LFS, nested repos,
  linked worktrees, generated files, migrations, databases, and secret-bearing files.
- Host-mediated commit/PR helpers. These must remain separate approvals and are not automatic.

## Open after v0.1 — open-source maturity

- Real public Release and signed/tagged artefacts (requires maintainer authorisation).
- Reproducible release workflow, provenance/SBOM, vulnerability scanning, and dependency bot.
- Compatibility policy based on real downstream projects rather than only synthetic fixtures.
- Maintainer triage SLA, governance, contributor roles, decision log, and deprecation policy.
- Documentation site, architecture decision records, screencast/GIF, and more use-case recipes.
- Real issues and PRs from outside contributors, response history, and published maintenance
  cadence. Stars, forks, and watches are discovery signals, not substitutes for this evidence.

## Explicitly not promised

- “Perfect” software, infallible attribution, safe autonomous self-modification, or guaranteed
  privacy from pattern matching.
- Automatic discovery of every relevant conversation or every root cause.
- Running arbitrary third-party code safely on a normal host without an isolation substrate.
- Automatic GitHub activity, marketing, telemetry, account actions, or eligibility for any
  external programme.
