# Changelog

All notable changes to this project are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

No changes have been assigned to the next candidate yet.

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

### Compatibility

- The released `v0.1.1`, packaged CLI, v1 schemas, package name, and frozen v0.1 safety contract
  remain compatible. This prerelease adds opt-in `review-init` and `review-check` commands;
  it does not discover Codex history or grant implementation authority.

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
