# Changelog

All notable changes to this project are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.1] - 2026-09-09

### Changed

- Renamed the public product display name to **Astra Skill Doctor** for GPT-6/Astra Skill adaptation.
- Kept the historical plugin id, package module, and CLI as compatibility entry points while exposing `gpt6-astra-skill`.
- Aligned repository-facing documentation, marketplace display names, and release notes with the new product identity.


Current local version source: `1.0.0`. This is a tested local stable candidate, not a tag or
GitHub Release.

### Fixed

- Reopened a narrowly scoped local qualification pass after the first real macOS dogfood exposed
  Homebrew Python's PEP 668 install boundary and an overly technical first-use path. The README
  now recommends the verified isolated `uv tool install .` route on macOS/Homebrew, confines
  normal `pip install .` to an activated virtual environment, and never recommends
  `--break-system-packages`.
- Split the installed plugin's newcomer path into two honest levels. A Codex host-selected quick
  audit needs no separate window, JSONL, scope root, or file path, but is explicitly
  `host-selected / unbound` and produces no CLI binding. The evidence-bound CLI path keeps its
  explicit sources, and v1 `review-init --mode audit` still requires start, end, and timezone.
- Added a fresh-task regression after real dogfood proved that an edited local marketplace source
  can differ from the versioned Skill snapshot actually loaded by Codex. Local iteration now
  requires an explicit remove/add refresh and a new task before the changed Skill is trusted.
- Rewrote the README around the product outcome, a 60-second Codex audit, the two review levels,
  exact local-plugin refresh, and a fact-bounded Codex-first position. Anthropic's public Skills
  examples remain packaging research only; no competitor text or code is copied.

### Compatibility

- No version, Python runtime, schema, CLI command, or authority boundary changed. Plugin manifest
  copy/default prompts changed to describe the two existing levels accurately. This local
  qualification update is not committed, pushed, tagged, released, or publicly submitted.

## [1.0.0] - 2026-08-30 (local stable candidate)

### Changed

- Promoted the independently security-reviewed RC surface without adding a feature or changing a
  schema, command, authority boundary, or runtime behavior.
- Finalised the stable Python package metadata and matching `1.0.0` skills-only Codex plugin.
- Replaced prerelease guidance with the stable core/plugin contract, local install workflow,
  platform-evidence boundary, and explicit separation from public publication.

### Verification boundary

- The full source and extracted-sdist suites, clean wheel/sdist installs, audit/daily/weekly
  workflows, exact binding/handoff positives and negatives, archive inspection, plugin validators,
  and a real local Codex marketplace add/install/remove cycle form the local stable gate.
- Windows-native API and failure-injection cases remain a required Windows CI gate; macOS skips are
  recorded and are not represented as Windows execution evidence.
- No commit, push, tag, Release, public CI run, plugin submission, promotion, or external message
  is part of this local candidate.

## [1.0.0rc1] - 2026-08-30 (local release candidate)

### Added

- `review-bind` for a private `review-binding/v1` identity over the exact final-report bytes,
  target, current verified source pack, candidate state, and integrity-bound timestamps.
- Read-only `review-handoff-check`, which reopens every explicit input and returns a stable ready
  marker only when report, source, candidate, target, and binding identities still agree.
- A Windows handle-relative output backend using a bound parent `HANDLE`,
  `NtCreateFile(RootDirectory=...)`, protected DACLs, delete-pending commit, same-domain parent
  revalidation, and handle-only rollback.

### Security and compatibility

- Incomplete evidence is blocked from normal handoff; the explicit archive override preserves an
  incomplete identity only and never grants implementation or external-action authority.
- Reports require visible, non-placeholder Markdown evidence. Hidden HTML comments, top-level or
  list/blockquote-contained fences, unknown frontmatter controls, target mismatches, stale heads,
  byte drift, in-place mutation, oversized persisted state, and insecure output primitives fail
  closed.
- v0.1, Alpha 3, Beta 1, and Beta 2 commands and schemas remain covered. Windows-native API tests
  are present but are honestly skipped on this macOS candidate pending a Windows CI runner.

## [0.2.0a3] - 2026-08-30 (local prerelease candidate)

### Added

- `codex-scan`, an opt-in command that binds exactly one explicit Codex JSONL export to a
  user-selected non-home scope root, target/task references, IANA timezone, and half-open window.
- A private `codex-input-envelope/v2` embedded in the evidence bundle. It records the exact source
  digest and byte size, hashed target/task bindings, physical record accounting, fixed
  inclusion/exclusion codes, and honest partial/unknown history coverage without retaining source
  text, file names, or paths.
- A strict scoped-input opener with ordinary component-level symlink/reparse rejection, hard-link
  rejection, POSIX `dir_fd`/`O_NOFOLLOW` traversal, and repeated identity checks. On macOS only,
  Apple's fixed root compatibility aliases are canonicalised to their root-owned `/private`
  targets.
- Official-source Codex alignment research covering Codex for OSS, Skills, `AGENTS.md`, approvals,
  plugins, and current compatibility implications.
- `codex-modern-normalization/v1` for the supported official `item_completed` TurnItem allowlist
  and `task_complete` / `turn_complete` terminals, plus a real named-Skill-shaped privacy fixture.

### Changed

- The dedicated Codex path captures at most 64 MiB and 1,000,000 physical records once and
  hashes/parses the same bytes; it does not enumerate the scope root or discover other history.
- Codex candidate windows now use the documented half-open `[start,end)` boundary, so an event
  exactly at `until` is excluded.
- Repeated completed-item snapshots now keep their first physical position while the latest valid
  structured snapshot supplies status. The same item ID in different turns remains distinct;
  ordinary messages and tool events are not content-deduplicated.
- Structured automation, delegation, Subagent, system, and non-evidence metadata records are
  counted explicitly instead of being inferred from prose.
- Snapshot IDs use canonical tuple hashing, retained/dropped item and terminal records are counted
  separately, and the envelope validator enforces exact conservation against recognized records.

### Security

- Filesystem roots, the user home itself, directories, parent traversal, scope escape,
  symlink/reparse components, hard links, input-boundary drift, and oversized Codex inputs stop
  before output creation.
- The envelope never upgrades one selected export into a claim of complete Codex task history;
  semantic normalization remains explicitly `partial-alpha.3` because the upstream protocol is
  non-exhaustive and this candidate uses a fixed allowlist.
- Missing/invalid timestamps, malformed records, unsupported records, and oversized records make
  the selected source and full evidence incomplete, so downstream analysis cannot confirm a
  candidate from partially normalised evidence.
- Control-bearing rollout IDs, unknown/malformed `UserInput` blocks, and invalid status/type pairs
  are unsupported rather than silently merged, discarded, or promoted to completed state.
- Hashing and parsing are bound to one captured byte buffer. Concurrent source-path stability is
  explicitly metadata-checked best effort rather than an atomic-snapshot claim; no network client
  is started, while remote-filesystem classification remains outside the envelope.
- Existing v0.1 `scan` behaviour remains available; the stronger Codex contract is an explicit new
  command and does not silently change the frozen v0.1 CLI path.

## [0.2.0b1] - 2026-08-30 (local prerelease candidate)

### Added

- Installed `review-init` support for all three useful modes: `audit`, `daily`, and `weekly`.
- Automatic daily and weekly half-open windows from an explicit IANA timezone, offset-aware
  reference timestamp, and local boundary hour, while retaining explicit start/end windows.
- Deterministic daylight-saving handling: nonexistent local boundary times advance to the first
  valid minute and repeated boundary times use their first occurrence.

### Security and compatibility

- Every generated scaffold remains zero-source, private, no-overwrite, analysis-only, and valid
  under the same `review-check` contract; no history discovery or network call was added.
- Legacy audit APIs and the audit CLI output marker remain compatible.
- Invalid modes, partial explicit windows, naive timestamps, conflicting reference/window inputs,
  invalid timezones, and invalid boundary hours fail without a traceback or output file.

## [0.2.0b2] - 2026-08-30 (local prerelease candidate)

### Added

- A strict private `candidate-ledger/v1` snapshot with stable opaque IDs, frozen transitions,
  target hashing, deterministic state heads, stale-head rejection, and exact unresolved carry-over.
- `source-pack` and read-only `source-verify` commands for path-free SHA-256 and byte-count binding
  of only the explicitly selected files below one non-home scope root.
- `candidate-sync` for no-overwrite private state updates from scoped `candidate-current/v1` input.
- A repository-local Codex marketplace and thin skills-only plugin that guides the installed CLI.

### Security and compatibility

- Candidate matching is exact by ID; the tool performs no semantic merge and does not silently
  drop unresolved `candidate`, `authorised`, `implemented-unverified`, or `regressed` entries.
- Scoped inputs reject roots/home, traversal, scope escape, links, hard links, duplicate physical
  files, replacement during read, excessive counts, and byte limits.
- Source packs retain no target text, paths, file names, source text, device, or inode metadata.
  Their digest proves byte identity only, not truth, authorship, completeness, or authority.
- The plugin contains no MCP, app, hooks, copied Python core, installer, or automatic updater.
  Missing or incompatible CLI versions are an explicit stop.

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
