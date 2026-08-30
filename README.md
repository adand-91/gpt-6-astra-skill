# Requirement Ledger AI

**Requirement Ledger has a stable explicit-evidence v0.1.1 and a public `v0.2.0-alpha.1`
prerelease for named-target audits.** When the host exposes bounded task history, name a Codex
conversation, Agent Skill, or project and the Skill can recover related context, prepare concrete
change cards, and compare the same case before and after an authorised edit. The Python package
does not yet ship its own Codex history adapter.

[![CI](https://github.com/adand-91/requirement-ledger/actions/workflows/ci.yml/badge.svg)](https://github.com/adand-91/requirement-ledger/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/adand-91/requirement-ledger)](https://github.com/adand-91/requirement-ledger/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.10--3.13-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[中文说明](README.zh-CN.md) · [v0.1 CLI contract](V0.1_CONTRACT.md) ·
[v0.2 host contract](V0.2_HOST_CONTRACT.md) ·
[Alpha 1 notes](docs/release-notes/v0.2.0-alpha.1.md) · [update map](UPDATE_MAP.md) ·
[roadmap](ROADMAP.md) · [open gaps](docs/PROJECT_GAPS.md) · [security](SECURITY.md)

> Requirement Ledger does not autonomously edit your project. The CLI gathers and structures evidence;
> Codex remains the developer, and every real modification stays visible and reviewable.

## Start with one sentence

After installing the Skill, the user names the target rather than diagnosing it:

> Use Requirement Ledger to audit this Skill. Find its related Codex history, tell me what should
> improve, preserve what already works, and show me the change cards before editing anything.

The Codex host should locate the target, find only its related authorised tasks and project
records, reconstruct the work history, explain the problems without jargon, preserve working
behaviour, prepare small change cards, and stop for authorisation before editing. The user does not
need to remember the failures or design YAML, prompts, tests, or repository architecture.

```text
one named target
  -> related Codex history
  -> repeated problems and personal preferences
  -> what must stay
  -> concrete change cards
  -> authorised visible edit
  -> same success and boundary cases before/after
```

See the [three review modes](references/review-modes.md),
[Codex context discovery](references/codex-context-discovery.md), the
[beginner Skill-personalisation workflow](references/personalization-workflow.md), and the fully
synthetic [walkthrough](docs/use-cases/improve-an-agent-skill.md).

## Three ways to use it

| Mode | Say this | What it does |
| --- | --- | --- |
| One-time audit | “Audit this conversation / Skill / project.” | Finds related history, prioritises problems, and prepares change cards |
| Daily review | “Review yesterday with Requirement Ledger.” | Reconstructs the previous workday, checks earlier changes, and recommends one improvement |
| Weekly review | “Run the weekly Requirement Ledger review.” | Deduplicates the week, checks maintenance health, and links relevant GitHub or official industry changes |

Alpha 1 installs the audit scaffold and checker only. Daily and weekly are documented host
contracts and reference templates, not initialisation modes in this prerelease. A one-time audit
stays on the named target. Future daily and weekly modes may enumerate Codex projects active only
in their explicit time window. If the host cannot retrieve history, it must ask the user to select
a task or bounded export rather than claim complete coverage.

Requirement Ledger AI is the guide and evidence layer, not a hidden patch bot.

## What v0.2.0-alpha.1 adds

- `review-init --mode audit` creates a private, analysis-only scaffold for one named target and
  explicit time window.
- `review-check` mechanically rejects malformed review contracts before they are treated as
  evidence or handed to an editing workflow.
- New files are no-overwrite and private-by-default where supported; initial coverage is honestly
  zero-source and incomplete.
- The [release notes](docs/release-notes/v0.2.0-alpha.1.md) explain the solved problems, while the
  [update map](UPDATE_MAP.md) separates shipped capability from the ten-day path to stable v0.2.

## Why this exists

AI-assisted projects usually lose the most valuable information they produce:

- the user corrects the agent, but the real requirement stays buried in chat;
- the same error appears again, but nobody can tell whether it is upstream, project-local,
  personal configuration, or still unknown;
- a patch is called “fixed” without a frozen baseline or the same after-test;
- useful feedback never reaches a maintainer, while unsafe raw logs get pasted into public
  issues.

Requirement Ledger makes that loop explicit:

```text
explicit Codex/Claude/text input + test log + read-only Git snapshot
  -> private evidence
  -> conservative attribution
  -> quote-free report + DRAFT repair plan
  -> host-owned Codex patch
  -> digest-bound oracle before/after result
```

It works with ordinary software projects. The target does not have to use AI, Python, or this
Skill; only the evidence collector itself is Python.

## What v0.1 delivers

- A zero-runtime-dependency package and `requirement-ledger` command for Python 3.10–3.13.
- Explicit Claude Code, Codex JSONL, and plain-text transcript adapters with event-level time
  filtering and input-mutation checks.
- A fixed, read-only Git snapshot: HEAD, status digest, dirty count, and tracked-file count;
  remote URLs are never read or emitted.
- Versioned `SourceRef`, `EvidenceItem`, `IssueRecord`, `FixProposal`, and `ValidationResult`
  records.
- Four attribution fields — `upstream`, `project-local`, `personal`, `unknown` — with
  `unknown` as the honest default.
- Physically separate private evidence and quote-free reports, restrictive file modes,
  non-overwrite writes, and a fail-closed privacy gate.
- `DRAFT — NOT SENT`, `not-applied` repair plans. No hidden patch, commit, push, Issue, PR,
  Release, upload, or telemetry.
- A deterministic, wholly synthetic end-to-end demo.

## Install

Clone the repository, then install the package locally:

```bash
git clone https://github.com/adand-91/requirement-ledger
cd requirement-ledger
python3 -m pip install .
requirement-ledger --version
```

The runtime uses only the Python standard library on systems with an IANA timezone database.
Windows installs the standard `tzdata` package conditionally because Windows does not ship that
database. Build isolation may fetch build tooling; a prepared offline Windows environment must
include `tzdata` before using `python3 -m pip install --no-build-isolation --no-deps .`.

To install this exact prerelease without cloning:

```bash
python3 -m pip install \
  https://github.com/adand-91/requirement-ledger/releases/download/v0.2.0-alpha.1/requirement_ledger-0.2.0a1-py3-none-any.whl
```

### Install the Codex or Claude Skill

The repository is also a self-contained agent Skill:

```bash
# Codex
git clone https://github.com/adand-91/requirement-ledger ~/.codex/skills/requirement-ledger

# Claude Code
git clone https://github.com/adand-91/requirement-ledger ~/.claude/skills/requirement-ledger
```

The Skill tells the host when to gather evidence, when to stop at a proposal, and how to hand a
reviewed plan back to the ordinary coding workflow. It does not grant new permissions.

## Sixty-second synthetic demo

This command does not inspect a repository, a home directory, or a real conversation:

```bash
requirement-ledger demo --output-dir /tmp/requirement-ledger-demo
find /tmp/requirement-ledger-demo -maxdepth 1 -type f -print
```

It writes five files:

```text
01-evidence.private.json   raw synthetic evidence; private format
02-analysis.json           conservative issue candidates
03-proposals.json          DRAFT — NOT SENT, not-applied plans
04-report.md               quote-free report; still needs human privacy review
05-validation.json         synthetic baseline-fail -> after-pass result
```

The source fixtures are in [examples/anonymous](examples/anonymous/README.md).

## Use it on a project

Choose the exact repository and exact evidence files yourself. Storing private evidence outside
the project is recommended:

```bash
requirement-ledger doctor --repo /path/to/project

requirement-ledger scan \
  --repo /path/to/project \
  --input /path/to/explicit-codex-or-claude-session.jsonl \
  --test-log /path/to/existing-test-output.log \
  --output /tmp/project-evidence.private.json

requirement-ledger analyze \
  --evidence /tmp/project-evidence.private.json \
  --output /tmp/project-analysis.json

requirement-ledger report \
  --analysis /tmp/project-analysis.json \
  --output /tmp/project-report.md

requirement-ledger suggest \
  --analysis /tmp/project-analysis.json \
  --output /tmp/project-proposals.json
```

`scan` never discovers `~/.codex`, `~/.claude`, or other projects. JSONL provider detection is
automatic; use `--provider codex|claude|text` when a custom filename is ambiguous. Time windows
are ISO-8601 and apply to individual JSONL events. Plain text has no timestamps, so it rejects
time-window flags instead of pretending.

### Record validation without running project code

v0.1 deliberately does not execute arbitrary third-party tests. Let Codex or your existing
sandbox freeze the exact argv, working directory, relevant environment, and fixture digests,
hash that descriptor with SHA-256, then run it before and after the reviewed intervention.
Provide the same 64-hex digest in both tiny JSON records and on the command line:

```json
{"oracle": "unit-regression", "oracle_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "exit_code": 1}
```

```json
{"oracle": "unit-regression", "oracle_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "exit_code": 0}
```

```bash
requirement-ledger verify \
  --oracle unit-regression \
  --oracle-digest aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  --baseline /tmp/baseline.json \
  --after /tmp/after.json \
  --output /tmp/validation.json
```

Only the same oracle name **and digest** changing from failure to success is `improved`.
Mismatched identities, boolean/non-integer exit codes, or codes outside 0–255 are
`inconclusive`; baseline success followed by failure is `regressed`.

## Attribution without pretending

Each issue stores a suspected scope and a final scope separately:

| Scope | What confirmation requires |
|---|---|
| `upstream` | independent projects/sessions, same provider/version, clean reproduction, local and personal causes excluded |
| `project-local` | direct repository evidence plus a clean comparison where the behaviour does not reproduce elsewhere |
| `personal` | separately authorised personal-configuration evidence or a clean-config comparison |
| `unknown` | the default when those conditions are not met |

A complaint is not an upstream finding. A failed project test is not proof that a dependency is
wrong. Incomplete or conflicting evidence blocks confirmation. See the normative
[v0.1 contract](V0.1_CONTRACT.md).

## Privacy and safety

Private evidence files may contain original user text and must end in `.private.json`; they are
created with restrictive permissions where the OS supports them. Do not attach them to an
Issue, PR, email, or chat.

Reports exclude original quotes, local paths, session IDs, command arguments, remotes, and raw
errors. Before a report is written, the automated gate checks common secret formats, auth and
cookie headers, email, phone, home paths, credential-bearing remotes, UUIDs, IP addresses, and
terminal controls. A hit returns `E_PRIVACY_BLOCK` and no report file is created.

**Passing an automated privacy check is not proof that a file is safe to share.** Every report
says that human review is still required.

The v0.1 CLI contains no project-code runner, patch application, dependency installer, network
client, telemetry, browser, GitHub writer, or account integration. Its only subprocesses are
fixed read-only probes through a trusted absolute Git executable with redirecting `GIT_*`
environment removed. Output parents must already exist; every output ancestor is checked before
an exclusive write. Read the [threat model](docs/THREAT_MODEL.md) and
[security policy](SECURITY.md) before using real evidence.

## Legacy retrospective tools

The original Skill workflow remains available for compatibility:

```bash
python3 scripts/scan_transcript.py path/to/session.jsonl
python3 scripts/check_retro_report.py path/to/report.md
python3 scripts/check_translation_sync.py
```

The legacy scanner can still discover local agent directories when explicitly invoked with
`--engine`. Its `--no-text` option only removes message/error bodies; paths, session metadata,
and command shapes may remain. It is **not share-safe**. Use the new packaged pipeline for any
new workflow and treat all legacy output as private.

## Development

```bash
python3 -m pip install --no-build-isolation --no-deps -e .
python3 -m unittest discover -s tests -v
python3 -m compileall -q src scripts tests
python3 scripts/check_translation_sync.py
```

All fixtures must be synthetic. Never paste a real transcript, secret, private remote, client
name, session identifier, or personal path into an Issue or test. See
[CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md), and the
[project gap ledger](docs/PROJECT_GAPS.md).

## What is intentionally unfinished

v0.1 does not provide safe autonomous modification. Isolation backends, object-bound approval
tokens, frozen-oracle execution, transactional apply, and rollback fault injection are required
before that boundary can move. Structured test adapters, clean-room reproduction, a packaged
Codex history adapter, real audit/daily/weekly validation, opt-in adoption evidence, governance,
and signed releases also remain open.

That list is maintained in [docs/PROJECT_GAPS.md](docs/PROJECT_GAPS.md), so “polished” cannot be
confused with “finished”.

## License

MIT. See [LICENSE](LICENSE).
