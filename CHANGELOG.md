# Changelog

All notable changes to this project are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

No changes yet.

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
