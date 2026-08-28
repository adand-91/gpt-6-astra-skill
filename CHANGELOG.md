# Changelog

All notable changes to this project are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

No changes yet.

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
- Repository text is pinned to LF for deterministic bilingual hashes on Windows, and transcript
  binding separates same-file identity from cross-platform-stable content metadata.
