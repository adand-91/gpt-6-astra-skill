# Changelog

All notable changes to this project are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

No changes yet.

## [0.2.0a3] - 2026-09-03 (prerelease)

### Added

- `codex-modern-normalization/v1` for the supported official `item_completed` TurnItem allowlist
  and `task_complete` / `turn_complete` terminals, plus a real named-Skill-shaped privacy fixture.

### Changed

- The dedicated Codex path now stops above 1,000,000 physical records as well as the existing
  64 MiB byte cap.
- Repeated completed-item snapshots keep their first physical position while the latest valid
  structured snapshot supplies status. The same item ID in different turns remains distinct;
  ordinary messages and tool events are not content-deduplicated.
- Structured automation, delegation, Subagent, system, and non-evidence metadata records are
  counted explicitly instead of being inferred from prose.
- Snapshot IDs use canonical tuple hashing, retained/dropped item and terminal records are counted
  separately, and the envelope validator enforces exact conservation against recognized records.

### Security

- The input envelope advances to `codex-input-envelope/v2`. Semantic normalization remains
  explicitly `partial-alpha.3` because the upstream protocol is non-exhaustive and this release
  uses a fixed allowlist.
- Control-bearing rollout IDs, unknown or malformed `UserInput` blocks, invalid status/type pairs,
  and normalization sub-counts that do not conserve fail closed rather than being silently merged,
  discarded, or promoted to completed state.
- Existing v0.1 `scan` and Alpha 2 `codex-scan` boundaries remain compatible; this prerelease does
  not discover tasks, read `~/.codex`, or claim that one selected export is complete history.

## [0.2.0a2] - 2026-09-01 (prerelease)

### Added

- `codex-scan`, an opt-in command that binds exactly one explicit Codex JSONL export to a
  user-selected non-home scope root, target/task references, IANA timezone, and half-open window.
- A private `codex-input-envelope/v1` embedded in the evidence bundle. It records the exact source
  digest and byte size, hashed target/task bindings, physical record accounting, fixed
  inclusion/exclusion codes, and honest partial/unknown history coverage without retaining source
  text, file names, or paths.
- A strict scoped-input opener with ordinary component-level symlink/reparse rejection, hard-link
  rejection, POSIX `dir_fd`/`O_NOFOLLOW` traversal, and repeated identity checks. On macOS only,
  Apple's fixed root compatibility aliases are canonicalised to their root-owned `/private`
  targets.
- Official-source Codex alignment research covering Codex for OSS, Skills, `AGENTS.md`, approvals,
  plugins, and current compatibility implications.

### Changed

- The dedicated Codex path captures at most 64 MiB once and hashes/parses the same bytes; it does
  not enumerate the scope root or discover other history.
- Codex candidate windows now use the documented half-open `[start,end)` boundary, so an event
  exactly at `until` is excluded.

### Security

- Filesystem roots, the user home itself, directories, parent traversal, scope escape,
  symlink/reparse components, hard links, input-boundary drift, and oversized Codex inputs stop
  before output creation.
- The envelope never upgrades one selected export into a claim of complete Codex task history;
  semantic normalization remains explicitly `partial-alpha.2` pending the next parser candidate.
- Missing/invalid timestamps, malformed records, unsupported records, and oversized records make
  the selected source and full evidence incomplete, so downstream analysis cannot confirm a
  candidate from partially normalised evidence.
- Hashing and parsing are bound to one captured byte buffer. Concurrent source-path stability is
  explicitly metadata-checked best effort rather than an atomic-snapshot claim; no network client
  is started, while remote-filesystem classification remains outside the envelope.
- Existing v0.1 `scan` behaviour remains available; the stronger Codex contract is an explicit new
  command and does not silently change the frozen v0.1 CLI path.

## [0.2.0a1] - 2026-08-30 (prerelease)

### Added

- A Codex-first host contract for one-time audits, daily improvement reviews, and weekly
  maintenance/ecosystem reviews. In this Alpha, only audit scaffold initialisation is exposed by
  the installed CLI; daily and weekly remain documented contracts and templates.
- Bounded Codex context-discovery rules: the user names a target or time window; the host finds
  related authorised history without requiring the user to restate the problems.
- Bilingual mode guidance and report templates for `audit`, `daily`, and `weekly`.
- A zero-dependency review-report contract validator with real ISO-8601 window ordering, IANA
  timezone checks, target-bound authorisation references, structured weekly-source fields, and
  English/Chinese template regression tests.
- A beginner-first Agent Skill personalisation workflow with a plain-language change card,
  preserved-behaviour inventory, success scenario, boundary scenario, and rollback.
- A bilingual, gate-driven ten-day update map from this Alpha to a stable `v0.2.0` decision.

### Changed

- The README and Skill now lead with context-aware personal improvement: name a conversation,
  Skill, project, or review window, then let Codex recover the related history.
- The `v0.2.0` roadmap now unifies the three requested uses in one project rather than three
  duplicate repositories.
- Scheduled daily and weekly runs are analysis-only by default; implementation and external
  actions still require current target-bound authority.

### Fixed

- A named target no longer has to be forced into the v0.1 project-evidence report shape before a
  review can begin: `review-init` creates a dedicated audit scaffold.
- Review documents no longer rely on visual completeness alone: `review-check` fails on invalid
  windows, timezones, required sections, evidence labels, candidate states, or authorisation
  declarations.
- The standalone checker no longer carries a second copy of the validation rules; it delegates to
  the packaged implementation.
- New review scaffolds fail instead of overwriting an existing output and use private file
  permissions where the platform supports them.
- Windows installs the standard `tzdata` database conditionally, so the same explicit IANA
  timezones validate on Linux, macOS, and Windows. A no-dependency Windows install now returns an
  actionable error instead of misreporting the missing database as an invalid timezone.

### Compatibility

- The released `v0.1.1`, packaged CLI, v1 schemas, package name, and frozen v0.1 safety contract
  remain compatible. This prerelease adds opt-in `review-init` and `review-check` commands;
  it does not discover Codex history or grant implementation authority. Unix-like systems keep
  zero runtime dependencies; Windows uses the conditional `tzdata` dependency required by
  Python's standard-library `zoneinfo` implementation.

## [0.1.1] - 2026-08-28

### Added

- Requirement Ledger AI positioning for AI project and Skill improvement workflows.
- A bilingual fifteen-day roadmap from the evidence prototype to the `v1.0.0` technical launch.
- A wholly synthetic, reproducible Skill-improvement walkthrough with an externally run,
  digest-bound before/after oracle.

### Changed

- README discovery metadata, badges, search terms, first-use framing, and links to the Skill case.
- Package metadata now derives the CLI and record version from one `__version__` source.
- Source distributions now explicitly include the bilingual roadmap.

### Compatibility

- The repository slug, package name, console command, CLI, schemas, and v0.1 safety boundaries
  are unchanged.

## [0.1.0] - 2026-08-28

### Added

- Installable zero-runtime-dependency package and `requirement-ledger` console command.
- Explicit-input Claude, Codex, and plain-text event normalisation.
- Versioned evidence, issue, proposal, and validation records.
- Read-only Git snapshots without remote inspection.
- Private evidence, conservative four-scope attribution, quote-free reports, and repair drafts.
- Synthetic end-to-end demo, CI matrix, Issue Forms, security/support/contribution policies,
  maintenance policy, threat model, architecture, scope ledger, and release checklist.

### Security

- New workflows never discover a home directory or run project code.
- Share-facing output has a fail-closed automated privacy gate and still requires human review.
- Repair suggestions are `DRAFT — NOT SENT` and `not-applied`.
- Generated feedback remains `DRAFT — NOT SENT` until a person sends it.
- Local actions remain proposals and are never automatically applied.
- No project-code execution, dependency installation, network, telemetry, commit, push, Issue,
  PR, Release, or upload is performed by the CLI.
- Repository text is pinned to LF for deterministic bilingual hashes on Windows. Transcript and
  test-log binding separate same-file identity from cross-platform-stable content metadata.
