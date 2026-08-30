# Review-mode design research

Checked 2026-08-29. This note records the narrow GitHub research used before adding the Codex-first
audit/daily/weekly host design. Stars are discovery signals, not quality verdicts.

## Repositories checked

### `nishantdesai/codex-history`

- Source: https://github.com/nishantdesai/codex-history
- Problem: read-only local Codex history search, inspection, export, and optional indexing.
- Structure: Rust CLI with direct grep, local index, structured output, redaction, release archives,
  and Homebrew packaging.
- Activity evidence: repository updated 2026-08-07; `v0.1.0` Release published 2026-03-12; MIT;
  9 stars and 1 fork at review time.
- Reuse: metadata-first search, read-only positioning, explicit opt-in for thinking/tool content,
  machine-readable output, and a separate index health command.
- Avoid: adding another mandatory runtime or copying an external index into the v0.1 core before
  the Codex host protocol is proven. Exported raw history remains private.

### `shinshin86/codex-history-list`

- Source: https://github.com/shinshin86/codex-history-list
- Problem: list local Codex sessions with time, recorded working directory, first user request,
  and source path.
- Structure: Node CLI that streams JSONL, stops after finding metadata, filters by date/cwd, and
  emits JSON.
- Activity evidence: repository updated 2026-08-19; MIT; 11 stars and 1 fork; no Release at review
  time.
- Reuse: resolve project identity from recorded cwd, perform metadata-first enumeration, use mtime
  only as a cheap prefilter, and keep JSON output for host orchestration.
- Avoid: its default full `~/.codex/sessions` scan as an implicit Skill action. Requirement Ledger
  must first bind a target or review window and must not expose full local paths in share reports.

### `haodehaode378/git-weekly`

- Source: https://github.com/haodehaode378/git-weekly
- Problem: aggregate commits across repositories into daily/weekly/monthly Markdown or JSON reports
  with optional LLM summarisation.
- Structure: Python CLI, multi-repository inputs, time-window filtering, conventional-commit
  categories, optional API-key-backed summarisation.
- Activity evidence: repository updated 2026-05-31; MIT; no stars, forks, or Release at review time.
- Reuse: explicit windows, multi-repository aggregation, Markdown/JSON separation, and small trend
  tables.
- Avoid: treating commits as the complete work record, making an API key a default dependency, or
  sending private work evidence to a remote model. There is not enough adoption evidence to reuse
  its implementation wholesale.

## Decision for Requirement Ledger

Use one repository and three host modes. Reuse metadata-first session discovery and explicit
windows as design patterns, but keep the released v0.1 CLI offline and explicit-input. Codex host
tools are the preferred discovery interface; a future packaged adapter must be separately scoped,
tested, and privacy-reviewed.

Weekly ecosystem evidence uses official GitHub repository data, Releases, changelogs,
documentation, and advisories before third-party news. Every item must carry URL and date. No
source can authorise a local change or external action.
