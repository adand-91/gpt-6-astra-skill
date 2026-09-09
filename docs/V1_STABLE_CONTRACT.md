# Requirement Ledger v1.0 Stable Contract

Status: the runtime/schema contract passed the local Beta/RC/Stable release train on 2026-08-30.
The `1.0.0` candidate was reopened on 2026-08-31 for a narrow Codex first-use and installed-plugin
snapshot qualification; no runtime or schema change is implied by that reopened gate.

## Product outcome

Requirement Ledger v1.0 is a privacy-aware, offline evidence and review tool for one
explicitly selected Codex task, Agent Skill, Git project, or bounded export.  It ships as:

1. a stable Python library and CLI that owns schemas, validation, privacy boundaries,
   candidate continuity, report binding, and deterministic verification; and
2. a thin, skills-only Codex plugin that guides the host to call the installed CLI.

The plugin is a distribution and workflow layer, not a second implementation.  The v1
plugin has no MCP server, app, hooks, plugin-owned authentication implementation or credential
flow, downloader, installer, model call, database, telemetry, or network dependency. The
marketplace's required `policy.authentication: ON_INSTALL` value is Codex host timing-policy
metadata; the plugin exposes no authentication method and handles no credential.

The plugin exposes two deliberately different review levels. A Codex host-selected quick audit is
an immediate, analysis-only, `host-selected / unbound` decision aid and creates no CLI artefact.
An evidence-bound review uses explicit files and the CLI chain below. Only the second level can
claim current source-pack, report, candidate-state, or handoff identity.

## Decision status

### Confirmed

- The local release train ends at a mechanically verified `1.0.0` candidate.
- The independent CLI/library remains the product core.
- The Codex distribution is a repository-local marketplace containing a skills-only plugin.
- Host-selected quick audit and evidence-bound CLI review are distinct levels; neither is described
  as the other.
- Inputs must be selected explicitly by the user or by a host that can prove a bounded
  selection.  The tool never discovers all history or all projects.
- Analysis does not authorize implementation, commit, publication, scheduling, or any other
  external action.
- No commit, push, tag, GitHub Release, promotion, programme application, public directory
  submission, or external message is part of this local train.

### Engineering decision

The smallest meaningful train is `0.2.0b1` -> `0.2.0b2` -> `1.0.0rc1` -> `1.0.0`.
Empty versions are forbidden: each prerelease must close a user-visible verification gap.

### Pending separate authority

Public plugin submission requires a later decision plus verified publisher identity,
review-ready public metadata and policy/support URLs, and separate authorization to submit
and publish.  Local validation is not public approval.

## Stable user workflow

The Codex-first quick path is:

```text
one host-selected task/project
  -> plain-language goal/stage/problem/preservation/first-change/next-action
  -> host-selected / unbound / analysis-only
```

It requires neither a synthetic time window nor private-file paths, but it does not create a
mechanically bound review. The evidence-bound path is:

```text
explicit target and time window
  -> explicit files inside an approved scope root
  -> private, hashed source pack
  -> audit/daily/weekly analysis-only review
  -> private candidate continuity state
  -> final report + exact-byte/source/head binding
  -> read-only handoff verification
  -> separately authorized host-owned implementation
  -> same-oracle outcome verification
```

No step silently grants the next step's authority.

## Release gates

### `0.2.0b1` — useful review cycles

- `review-init` supports `audit`, `daily`, and `weekly`.
- Explicit windows remain supported.
- Daily and weekly windows can be computed from an explicit IANA timezone, reference
  timestamp, and local boundary hour.
- DST, month/year boundaries, exact-boundary semantics, bad timezones, and invalid hours are
  tested.
- Scaffolds remain zero-source, private, analysis-only, and pass the same report checker.

### `0.2.0b2` — traceable continuity and Codex distribution

- A private candidate ledger uses stable opaque IDs, an explicit transition table,
  deterministic heads, target binding, stale-head rejection, exact carry-over, and no silent
  deduplication or drop.
- A private source pack binds only explicitly named scoped inputs by digest and byte count; it
  stores neither source text nor local paths.
- A repository-local marketplace exposes a thin skills-only Codex plugin and performs an
  installed-CLI version preflight without installing or updating anything.

### `1.0.0rc1` — frozen release surface

- A final review can be bound to its exact report bytes, source pack, target, candidate head,
  and review metadata.
- A read-only handoff check reopens every explicit input, rejects changes, and prints a stable
  ready/not-ready result without writing.
- Private outputs use no-overwrite writes and restrictive permissions where supported.
- Legacy v0.1 and Alpha 3 commands and schemas continue to pass their test suites.
- The release candidate passes the local supported Python/OS target, clean wheel and sdist builds,
  clean installs, privacy checks, and plugin validators. Cross-platform CI is configured, but a
  public Linux/Windows matrix is a later publication gate and is never inferred from local skips.

### `1.0.0` — stable promotion

- No feature is added after RC.  Only release metadata and documentation may change; any code
  correction requires rebuilding and revalidating the RC first.
- The local source suite collected 194 tests: 187 passed and seven Windows-native tests were
  explicitly skipped on macOS. The extracted sdist collected the same 194 tests, with the three
  repository-only plugin checks plus those seven Windows-native checks explicitly skipped.
- The final wheel, sdist, source snapshot, test counts, smoke results, and SHA-256 hashes are
  recorded in a local release-evidence directory.
- Three maintainer-owned bounded workflows (audit, daily, weekly) and positive/negative plugin
  cases pass without broad discovery, raw private evidence in chat, automatic edits, or
  external actions.

## Normative safety and compatibility rules

- Scope roots cannot be a filesystem root or the user home directory.
- Scoped inputs must be explicit regular files below the scope root; links, traversal, hard
  links, replacement during read, and duplicate aliases fail closed.
- Every private schema is size- and count-bounded and rejects unknown or malformed control
  fields.
- Target identity is represented by a digest in private machine state.  A digest proves byte
  identity only; it does not prove truth, authorship, quality, or authorization.
- Candidate matching is exact by host-supplied opaque ID.  v1 performs no semantic merge.
- Unresolved candidates absent from the current input are carried forward and identified as
  carried; they are never silently discarded.
- Review binding requires `status: final`, a mechanically valid report, and current explicit
  sources.  It does not authorize the proposed change.
- The plugin treats `requirement-ledger --help` as the installed command authority.  Missing or
  incompatible CLI versions produce an actionable stop; the plugin never installs software.
- A host-selected quick audit does not call `review-init` or claim a binding. In v1, an
  evidence-bound CLI `review-init --mode audit` still requires explicit start, end, and timezone.
- Editing a local marketplace checkout does not itself prove which versioned Skill snapshot Codex
  loaded. Qualification refreshes the installed plugin, starts a new task, and verifies the
  current contract before claiming the plugin path passed.
- Python CLI and Codex plugin are separate distribution layers and must not embed one another.
- Windows output creation uses a bound parent `HANDLE`, `NtCreateFile(RootDirectory=...)`, a
  protected DACL, and handle-only rollback. Windows-native execution evidence must come from a
  Windows runner; macOS contract tests cannot be reported as that evidence.

## Stable exclusions

v1 does not include automatic task/history discovery, background monitoring, network trend
collection, model-based scoring, semantic candidate matching, automatic project edits, auto
commit/push/release, GUI, hosted service, database, remote trace export, OAuth, MCP, Apps SDK
widgets, or IDE-extension guarantees.

## Research basis and reuse boundary

- OpenAI's plugin documentation supports skills-only plugins, a required
  `.codex-plugin/plugin.json`, and repository-local marketplaces.  MCP is reserved for live
  external capabilities, authentication, or controlled remote tools; none is needed here.
- `openai/codex` supports the architectural pattern of separating durable records, visible
  summaries, checkpoints, and explicit state transitions.  v1 does not embed Codex internals.
- `anthropics/skills` is useful packaging research, not this project's runtime or standard.
  Requirement Ledger is Codex-first, adds a deterministic CLI beyond instruction text, depends on
  no Claude-specific hook/plugin/configuration, and copies no Anthropic Skill text or inconsistently
  licensed code. This is an architectural distinction, not a universal host-quality claim.
- `promptfoo/promptfoo` supports repeatable machine checks plus human-readable reports.  v1
  does not import its providers, model execution, web UI, or runtime.
- `Arize-ai/phoenix` supports separating original events from derived summaries.  v1 does not
  import telemetry, databases, remote MCP, deployment infrastructure, or Elastic-licensed
  code.
- `openai/openai-apps-sdk-examples` demonstrates narrow tool contracts, but its MCP/widget
  runtime would expand v1's permissions and is intentionally excluded.

Only public architectural ideas are reused.  No external runtime or source code is vendored.
