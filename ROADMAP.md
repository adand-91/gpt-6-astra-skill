# Roadmap

Requirement Ledger AI is moving from a released evidence prototype to a focused, usable
`v0.2.0` in a ten-day, gate-driven sprint. Dates are targets, not permission to ship unfinished
or fabricated activity. Every public version must represent a coherent, tested capability.

[中文路线图](ROADMAP.zh-CN.md) · [ten-day update map](UPDATE_MAP.md) ·
[open gaps](docs/PROJECT_GAPS.md)

## Product destination

Stable `v0.2.0` is an AI project and Agent Skill feedback loop:

```text
named Codex target or review window
  -> related authorised history + explicit Git/test evidence
  -> private, traceable findings
  -> one-time, daily, or weekly improvement report
  -> reviewed host-owned Codex change
  -> same-oracle before/after evidence
```

The Codex host performs bounded related-context discovery. The CLI remains the explicit-file
evidence and validation layer. Neither silently scans unrelated history, runs project code, edits
a worktree, or performs GitHub/account actions.

“Complete in ten days” means a stable and useful v0.2 contract, package, three-mode workflow,
documentation, examples, CI, and release evidence. It does not mean every future integration,
provider, or personal workflow is finished.

## Ten-day v0.2 completion track

### `v0.2.0-alpha.1` — installable named-target audit

- Private, no-overwrite `review-init --mode audit` scaffold for one explicit target and window.
- Zero-dependency `review-check` with structured report, evidence, timezone, and authority gates.
- Bilingual host contract, reference templates, release notes, and update map.
- The released v0.1.1 evidence CLI remains compatible.

Exit gate: both artefacts install cleanly, the audit command path passes, notes and checksums match
the public assets, and the tagged commit passes cross-platform CI.

### `v0.2.0-alpha.2` — bounded Codex input target

- Explicit selection of one Codex export or host-provided source set.
- Honest coverage and exclusion records; no unrelated-history or home-directory scan.
- Modern Codex export shapes normalised without weakening the v0.1 explicit-input boundary.
- A second maintainer-owned named-Skill case showing relevance and false-match control.

Exit gate: a non-expert can name a target, supply or approve a bounded source set, and understand
what was read, excluded, preserved, inferred, and left unknown.

### `v0.2.0-beta.1` — installed three-mode review loop target

- Installed initialisation and checking for one-time, daily, and weekly reviews.
- Exact workday/week windows, IANA timezone handling, and source-bound ecosystem evidence.
- Stable candidate identities, carry-over, and duplicate suppression across repeated reviews.
- Scheduled use remains analysis-only; implementation still needs visible current authority.

Exit gate: all three modes produce traceable reports from the installed package and a repeated run
does not silently drop or duplicate unresolved candidates.

### `v0.2.0-rc.1` — bound review handoff target

- Private review packs bind target, sources, candidate state, and exact final report bytes.
- The approved report is revalidated immediately before the Codex implementation handoff.
- Mismatch, stale report, missing source, or changed target fails closed.
- One visible change card preserves working behaviour and defines success, boundary, rollback, and
  disproof cases.

Exit gate: the report handed to Codex is provably the report approved by the user, and the same
case can be compared before and after without granting hidden authority.

### `v0.2.0-rc.2` — complete launch candidate target

- Linux, macOS, and Windows CI for Python 3.10–3.13.
- Clean wheel/sdist installs, deterministic demos, path/privacy gates, and migration notes.
- Synthetic one-time/daily/weekly demos plus maintainer-owned real-use evidence.
- README, Skill, package metadata, schemas, limitations, and release assets agree on one commit.

Exit gate: every v0.2 promise passes the release checklist on the same commit. Any failed gate
stops the stable release.

### `v0.2.0` — stable three-mode product decision

The release candidate becomes `v0.2.0` only when its code, documentation, examples, packages,
public CI, and post-download checks agree. Stable means a dependable product promise, not
autonomous editing or perfect diagnosis.

The detailed day-by-day order and gates are in the [update map](UPDATE_MAP.md).

## Beyond v0.2

- `0.2.x`: compatible bug, privacy, parser, packaging, and documentation fixes backed by evidence.
- `0.3.0`: opt-in deterministic Skill-health scanning only after the v0.2 review loop has real-use
  evidence and the scanner's boundary is independently validated.
- `1.0.0-rc.1`: stable public contracts and migration path for every promise intended for 1.0.
- `1.0.0`: only after the full stable contract passes on one public commit.

Human-confirmed semantic grouping, structured test adapters, additional providers, and opt-in
adoption records remain future work. There is no fixed patch-release count: real Issues,
reproductions, security needs, and coherent features drive releases; a no-change period creates no
Git noise.

## Explicitly outside the v0.2 sprint

- Unattended code or Skill modification.
- Automatic commit, push, Issue, PR, Release, upload, or telemetry.
- A web account system, hosted dashboard, or team permissions.
- Claims that a pattern-based privacy check makes an artefact safe to share.
- A general-purpose sandbox, transactional apply, or automatic rollback engine.
