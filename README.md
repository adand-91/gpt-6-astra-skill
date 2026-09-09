# Astra Skill Optimizer

### Astra Skill Optimizer compatibility and personal workflow optimization

Astra Skill Optimizer adapts existing project Skills and workflows when new GPT-6/Astra model behavior makes older constraints unreliable. Select one project and its related Skills; the workflow produces evidence-bound findings, minimal changes, and reproducible validation. Long term it becomes a Jarvis-like personal and community Skill optimization system.

Plain language here does not mean the shortest possible answer. It means a decision-complete
explanation: conclusion first, then enough evidence, impact, action, and acceptance detail for the
user to understand the problem without translating jargon or asking what the report means.

**Astra Skill Optimizer is the current public product and repository identity.** The legacy Python package and CLI remain as compatibility entry points during migration.

**The public identity is Astra Skill Optimizer.** The existing Python package and CLI remain compatibility entry points during the naming migration. The current plugin is a thin Skill workflow; complete GPT-6/Astra adaptation still requires real project feedback.

[中文说明](README.zh-CN.md) · [product completion contract](docs/V1_PRODUCT_CONTRACT.md) ·
[stable contract](docs/V1_STABLE_CONTRACT.md) ·
[roadmap](ROADMAP.md) · [security](SECURITY.md) · [Codex alignment](docs/CODEX_ALIGNMENT_RESEARCH.md)

> The repository naming migration and public metadata alignment are tracked separately from historical release records.

## Why it exists

Long AI-assisted projects lose decisions inside chat: the current goal drifts, old requirements
reappear as facts, useful behaviour gets removed during a fix, and a digest is mistaken for proof
that a report is true or approved. Astra Skill Optimizer gives GPT-6/Astra workflows a narrow compatibility loop:

```text
one selected target
  -> goal and current stage
  -> main problem and preserved behaviour
  -> one reviewable improvement
  -> explicit next action and authority
  -> optional exact-source binding and handoff check
```

It does not discover every task, scan a home directory, edit the target, or turn analysis into
permission.

## Fast Codex project takeover

Install the core and plugin, select one Codex task or project, then start a new task and say:

```text
Hi Jarvis, take over this selected project. Recover its goal, current
stage, blocker, and one next action. Do not modify it.
```

If the host does not select the Skill automatically, retry once explicitly:
`$requirement-ledger-workflow Hi Jarvis, take over this selected project.`

The first screen should look like this—not like a request for JSONL paths or schema fields:

```text
# Project goal
...
## Overall progress: about 60% (estimated)
██████░░░░
Current work area: ...
## Current-area progress: about 80% (estimated)
████████░░
Current blocker: none.
No decision is needed from you now.
# Next step
...
Completion test: ...
```

This quick result is a `host-selected / unbound` Codex decision aid. Evidence or authority appears
in plain language only when it changes the next action; the first screen has no fixed technical
metadata line. It is not a CLI-created source pack, final report, or handoff identity.

## Three answer depths

Jarvis does not print the complete project card after every message.

| What you need | What Jarvis returns |
| --- | --- |
| One narrow answer | The answer first, plus only the decisive reason or practical effect. |
| A clear explanation | Conclusion, necessary cause or evidence, practical impact, and what follows. |
| Takeover, complete status, or a key project event | The full eight-field report with both progress bars, one next action, and its completion test. |

Daily and weekly reports keep their own fixed layouts. The daily report ends with one
highest-value next action; the weekly report may rank up to three next-period actions. Neither
mode mechanically prepends the ordinary project card.

## Six project-manager scenes

Jarvis chooses one primary scene from ordinary language. It does not ask the user to select an
internal workflow first.

| What the user says | Primary scene | Useful result |
| --- | --- | --- |
| “Take over this project.” | Project setup | Goal, stage, evidence freshness, authority, blocker, and first action |
| “What changed today?” | Progress review | Period, completed work, change, risk, and one next-period priority |
| “The client changed the requirement.” | Requirement change | Old/new requirement, impact, invalidated assumptions, decision, and safe next action |
| “Why is this blocked?” | Blocker diagnosis | Symptom, facts, reproduction state, candidate causes, missing evidence, and next check |
| “Can this version ship?” | Version acceptance | Scope and criteria with pass/fail/skipped/unknown kept separate |
| “Prepare a handoff.” | Handoff | Goal, decisions, unfinished work, risks, evidence pointers, and receiving-task opening |

An ordinary report offers at most three prompts relevant to the current stage. The complete menu
appears only when the user asks what Jarvis can do. For unfamiliar implementation work, Jarvis can
first check available Skills, official tools, original GitHub projects, documentation, and relevant
public forums, then explain what is worth reusing. Discovery does not itself install or run a
candidate. Visible user corrections and reproduced failures can become focused improvement
candidates; Jarvis does not claim passive observation, automatic memory, or background learning.
Daily and weekly reports can run on demand; unattended delivery still needs a separately configured
schedule and notification path.

## Two review levels

| Level | Use it when | Inputs | Honest result |
| --- | --- | --- | --- |
| **Codex quick audit** | You need the next maintenance decision now. | One host-selected task or project. No separate window, JSONL, scope root, or file path. | Plain-language, `analysis-only`, `host-selected`, `unbound`; dynamic state is `partial`, `unstable`, or `unknown` until verified. |
| **Evidence-bound review** | The result must be reproducible or handed off. | Explicit target, half-open window, IANA timezone, non-home scope root, exact files, and optional candidate state. | Private source pack, checked final report, exact binding, and read-only handoff verification. |

The v1 CLI's `review-init --mode audit` remains part of the second level and therefore still
requires explicit `--start`, `--end`, and `--timezone`. The plugin must never imply that a quick
audit already passed the evidence-bound chain.

The complete target experience and its release gates are defined in the
[Jarvis v1 product completion contract](docs/V1_PRODUCT_CONTRACT.md). The local Python version
`1.0.0` is the stable technical core; it is not, by itself, proof that every product gate or
public-release gate has passed.

## Why Codex-first

- The entry point is one selected Codex task or project and one explicit Skill invocation—not a
  new form the user must learn before receiving a useful answer.
- The plugin is a thin, skills-only Codex distribution layer. Deterministic schemas, privacy
  boundaries, stale-state rejection, exact-byte binding, and verification stay in an ordinary
  Python CLI that can be tested independently.
- Host text, repository instructions, tool output, and old reports remain evidence, never fresh
  authority. That matches Codex's explicit approval and layered-instruction model.
- This is not a Claude Code port. Anthropic's public Skills examples informed packaging research
  only; v1 depends on no Claude-specific hook, plugin runtime, or configuration, and copies no
  Anthropic Skill text or code. The differentiator is executable verification beyond instructions,
  not a blanket claim that one coding agent is universally better.

See the fact/decision/unknown split in [Codex alignment research](docs/CODEX_ALIGNMENT_RESEARCH.md).

## Architecture

```text
Codex host-selected context --quick audit--> plain-language, unbound decision

explicit target/window/files
  -> independent requirement-ledger CLI
  -> source pack + candidate continuity + final report
  -> exact review binding + read-only handoff check
  -> separately authorised host-owned implementation
```

The repository-local plugin is a thin Skill distribution layer with no second runtime, app, hook, plugin-owned
authentication or credential flow, updater, model call, telemetry, database, or network client.
The normative boundary is [the v1 stable contract](docs/V1_STABLE_CONTRACT.md).

## Install the core locally

### macOS with Homebrew Python

From this checkout, use an isolated tool environment:

```bash
uv tool install .
requirement-ledger --version
```

This exact macOS checkout installed `requirement-ledger 1.0.0` through `uv tool install .`.
Homebrew-managed Python follows PEP 668 and can reject system-level `pip install`; do not use
`--break-system-packages` for this project.

### Existing virtual environment

```bash
python3 -m pip install .
requirement-ledger --version
```

The core uses the Python standard library. Windows installs also receive the small conditional
`tzdata` package so IANA review windows remain available. The old public Alpha wheel is not this
local candidate.

## Install or refresh the local Codex plugin

```bash
codex plugin marketplace add /absolute/path/to/requirement-ledger
codex plugin add requirement-ledger@requirement-ledger-local
codex plugin list --marketplace requirement-ledger-local
```

Codex installs a versioned plugin snapshot. During local development, editing this checkout does
not prove that a new task loaded the changed Skill bytes. If the same unpublished version was
already installed, refresh it explicitly and then start a new Codex task:

```bash
codex plugin remove requirement-ledger@requirement-ledger-local
codex plugin add requirement-ledger@requirement-ledger-local
```

Use `codex plugin --help` as the installed command authority. Removing the plugin does not
uninstall the Python package.

## Evidence-bound CLI workflow

Keep the private source pack, candidate state, report, and binding under one approved non-home
scope. Every placeholder below must be replaced with one explicit local value.

```bash
# 1. Create and validate a bounded audit scaffold.
requirement-ledger review-init --mode audit --target project:example \
  --start 2026-08-01T08:00:00+08:00 --end 2026-08-02T08:00:00+08:00 \
  --timezone Asia/Shanghai --output /approved/review/final-report.md
requirement-ledger review-check /approved/review/final-report.md

# 2. Bind only the selected files, then verify their current bytes.
requirement-ledger source-pack --target project:example --scope-root /approved/review \
  --source /approved/review/input.jsonl --output /approved/review/sources.private.json
requirement-ledger source-verify --pack /approved/review/sources.private.json \
  --target project:example --scope-root /approved/review \
  --source /approved/review/input.jsonl

# 3. Carry exact candidate state, check the completed report, bind it, and recheck the handoff.
requirement-ledger candidate-sync --target project:example --scope-root /approved/review \
  --current /approved/review/current-candidates.private.json \
  --output /approved/review/candidates.private.json
# After replacing the scaffold with a complete status=final report:
requirement-ledger review-check /approved/review/final-report.md
requirement-ledger review-bind --target project:example --scope-root /approved/review \
  --report /approved/review/final-report.md --source-pack /approved/review/sources.private.json \
  --source /approved/review/input.jsonl --candidate-state /approved/review/candidates.private.json \
  --output /approved/review/review-binding.private.json
requirement-ledger review-handoff-check --binding /approved/review/review-binding.private.json \
  --target project:example --report /approved/review/final-report.md \
  --source-pack /approved/review/sources.private.json --scope-root /approved/review \
  --source /approved/review/input.jsonl --candidate-state /approved/review/candidates.private.json
```

`review-handoff-check` blocks incomplete evidence by default. `--allow-incomplete-archive` retains
an incomplete identity for archival use only; it does not authorise implementation or publication.

## Compatibility and boundaries

- The v0.1 CLI remains available for explicit evidence, conservative attribution, draft repair
  plans, and externally recorded before/after oracle results.
- The CLI does not run project code, apply a patch, modify a worktree, commit, push, create issues,
  publish a release, upload data, or use telemetry.
- Private evidence and source packs can contain sensitive relationships or hashes. A mechanical
  pass is not publication approval.
- A SHA-256 digest proves byte/state identity within the selected inputs. It does not prove truth,
  authorship, completeness, semantic correctness, approval, or execution authority.
- Windows-native fault-injection tests have not yet run on Windows for this candidate; macOS skips
  are not cross-platform evidence.

Before automating the workflow, read the [stable contract](docs/V1_STABLE_CONTRACT.md),
[threat model](docs/THREAT_MODEL.md), and [release checklist](docs/RELEASE_CHECKLIST.md).
