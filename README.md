# requirement-ledger

**A local, privacy-first evidence loop for improving any Git project with Codex or another
coding agent.** It turns the conversations, errors, Git state, and test results you explicitly
give it into traceable issue candidates, repair plans, and before/after evidence.

[中文说明](README.zh-CN.md) · [v0.1 contract](V0.1_CONTRACT.md) ·
[open gaps](docs/PROJECT_GAPS.md) · [security](SECURITY.md)

> v0.1 does not autonomously edit your project. The CLI gathers and structures evidence;
> Codex remains the developer, and every real modification stays visible and reviewable.

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

The runtime uses only the Python standard library. Build isolation may fetch build tooling;
for a prepared offline environment use `python3 -m pip install --no-build-isolation --no-deps .`.

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
before that boundary can move. Structured test adapters, clean-room reproduction, daily/weekly
reports, opt-in adoption evidence, governance, and signed releases also remain open.

That list is maintained in [docs/PROJECT_GAPS.md](docs/PROJECT_GAPS.md), so “polished” cannot be
confused with “finished”.

## License

MIT. See [LICENSE](LICENSE).
