# Astra Skill Doctor v1 product completion contract

Legacy reference: Jarvis v1 product completion contract.

This document defines the public product experience for Astra Skill Doctor. It records the product contract; it does not authorize a new release.

## Name and version boundary

- The public product and GitHub repository are **Astra Skill Doctor** (`gpt-6-astra-skill`). The legacy
  Requirement Ledger package, CLI, and plugin entry points remain compatibility names during migration.
- The historical local `1.0.0` candidate proves the Python CLI and evidence workflow. It does not by
  itself prove that GPT-6/Astra adaptation works across real projects.
- “v1 complete” below means both the conversational product and its release evidence pass their
  gates. Local product work can finish before public release actions are authorized.

## What changes after installation

A newcomer selects one Codex project or task and says:

`Hi Jarvis, take over this project.`

Astra Skill Doctor then:

1. answers immediately before reading tools or files: Chinese takeover starts with `可以接管。`,
   while a Chinese progress request uses only `可以汇报。` as its pre-tool acknowledgement;
2. restores the goal and latest checkpoint from bounded project context;
3. shows one decision-ready eight-field progress report with a fixed visual hierarchy;
4. asks only questions whose answers would change the next action, with no more than three at once;
5. selects one primary lifecycle scene and recommends exactly one next action;
6. after the user authorizes that action, performs the bounded work and reports at observable
   stage events without requiring a separate progress prompt;
7. records a fresh checkpoint so another task can continue reliably; and
8. offers the evidence-bound CLI only when reproducibility, acceptance, dispute, or handoff
   requires exact inputs and byte identity.

The user should not need to know the CLI, schema, repository layout, or internal Skill structure to
receive the first useful result.

For an ordinary takeover or progress request, Jarvis stops after that report. When project
`CONTEXT.md` is a short index, it may follow its one active current-context pointer as the bounded
checkpoint. It does not browse the surrounding context collection or related tasks, start a
duplicate Worker review, or wait on running work merely to restate that checkpoint. Running results
stay `unknown` or `unstable` until fresh evidence arrives.

## Project state and report

On first takeover, Jarvis tracks four state values internally:

- selected project or task;
- evidence freshness: `fresh`, `stale`, or `unknown`;
- current authority: `analysis-only` or the exact bounded action the user authorized; and
- primary lifecycle scene.

These values no longer form a fixed bilingual metadata line. Explain them in plain language only
when they change the conclusion or next action.

The eight report meanings remain authoritative: project goal, overall progress, current work area,
work-area progress, blocker, required user decision, one next action, and its completion test.
Goal, a required decision, and the next action receive the strongest emphasis; both progress values
use secondary headings; work area, an ordinary blocker, and “no action needed” remain normal text.
Missing evidence stays visible as `UNKNOWN`; it is never replaced by an inference.

## Plain-language completeness

Plain language is not a minimum-word-count target. A report is complete when the user can understand
the conclusion, decisive evidence, cause or practical impact, next action, and completion test
without translating jargon or asking what the report means. Detail scales with the decision: a
simple status can be brief, while a technical blocker or release judgment must retain the reasoning
and evidence needed to act safely. Remove repetition, irrelevant implementation detail, unexplained
jargon, metaphors, and slogans; do not remove necessary technical terms, facts, inferences, unknowns,
coverage, or authority boundaries. Reuse vocabulary already established with the user instead of
re-teaching it in every report.

Jarvis uses three answer depths. A narrow question gets a direct answer plus only the decisive
reason or practical effect. A request to explain gets the conclusion, necessary evidence or cause,
impact, and the action that follows. A takeover, complete progress request, or project-steering
event gets the full eight-field report. The full report is not repeated after every follow-up merely
because Jarvis manages the project.

## Six lifecycle scenes

Jarvis routes each turn to one primary scene. If a message contains several intents, it chooses the
one that changes the next action and briefly queues the others instead of printing several reports.

1. **Project setup** — recover or establish the goal, scope, stage, evidence freshness, authority,
   blocker, and first action.
2. **Progress review** — report the chosen period or current stage, completed work, changes, risk,
   and one next-period priority. Without comparable history, state that change is unknown.
3. **Requirement change** — separate the previous requirement, new requirement, source, affected
   scope, invalidated assumptions, decision needed, and safe next action. Do not silently write the
   change back or implement it.
4. **Blocker diagnosis** — separate symptom, observed facts, reproduction state, candidate causes,
   missing evidence, and the next diagnostic check. Do not present a candidate cause as proven.
5. **Version acceptance** — report scope and criteria with `pass`, `fail`, `skipped`, and
   `unknown` kept separate. A skipped or untested check never counts as passed or as release
   authority.
6. **Handoff** — preserve goal, stage, completed work, decisions, unfinished work, risks and
   unknowns, next action, evidence pointers, and one opening sentence for the receiving task.

After an ordinary report, show at most three short, current-stage suggestions. Show the complete
six-scene menu only when the user asks what Jarvis can do.

## Additional product capabilities

These capabilities belong to the completed product, but they remain separately bounded:

- **Reusable-resource research:** before unfamiliar or substantial implementation, Jarvis can
  recommend a bounded search across GitHub, official documentation, and relevant public forums.
  It records sources and reuse decisions, and does not install, clone, run, or copy a candidate
  without the required authorization and licence check.
- **Daily and weekly review:** Jarvis can produce an on-demand daily or weekly report from available
  evidence. Each mode keeps its own established section order instead of receiving the routine
  eight-field project card. A daily report ends with one highest-value next action; a weekly report
  may retain up to three ordered next-period actions. Unattended delivery requires a separately
  configured schedule and notification path.
- **Authorized progression:** one user goal does not grant unlimited authority. Jarvis can continue
  through the approved work package, report stage changes and deviations, then request a new
  decision when scope or risk materially changes.
- **Self-improvement:** repeated feedback and verified failures become improvement candidates.
  Jarvis can propose a focused Skill or program change, but implementation, commit, and release
  remain distinct actions.

## Two product layers

| Layer | Default use | Result |
| --- | --- | --- |
| Conversational project manager | Ordinary takeover, progress, change, diagnosis, acceptance, and handoff | Fast, plain-language, `host-selected / unbound`, with fact/inference/unknown separated |
| Evidence-bound CLI | Reproducibility, disputed claims, formal acceptance, or durable handoff identity | Explicit private inputs, deterministic validation, exact binding, and read-only verification |

The conversational layer must not pretend it has passed the evidence-bound layer. The CLI must not
be dumped into the first screen merely because it exists.

## Completion gates

Astra Skill Doctor v1 is product-complete only when all of these are true:

1. A fresh Chinese takeover begins visibly with `可以接管。`; a Chinese progress request uses only
   `可以汇报。` before tool use. Both respect the bounded first-pass read budget and ordinary reports
   do not expand into central-context browsing, related-task reads, duplicate Worker review, or
   waiting; following one active checkpoint pointer is allowed.
2. Direct, explained, and full-report answers route by the user's information need; ordinary
   follow-ups do not mechanically repeat the full dashboard.
3. Project state and the eight-field report work with complete, stale, and missing evidence while
   preserving the agreed visual hierarchy.
4. Plain-language reports are decision-complete rather than artificially short; the WQ regression
   keeps the evidence and reasoning needed to understand the recommendation.
5. All six lifecycle scenes have one primary route, realistic paraphrase tests, a success case,
   and a boundary case.
6. Daily and weekly reports preserve their own canonical section order; daily has one
   highest-value next action and weekly has no more than three ordered next-period actions.
7. Multi-intent requests produce one report and one next action; ordinary first screens show no
   more than three current-stage suggestions.
8. Requirement changes do not auto-write, blocker diagnoses do not auto-fix, and version
   acceptance does not count skipped or unknown checks as passed.
9. High-impact claims without fresh evidence are downgraded to `UNKNOWN`; an evidence upgrade is
   suggested but never run without the required explicit inputs and authority.
10. Resource discovery and feedback-driven improvement stay bounded: candidates are evidenced,
    no passive observation is claimed, and installation or implementation follows normal authority.
11. The full source suite, plugin validation, translation checks, source/cache identity, and fresh
    Codex dogfood pass without expanding the runtime or authority boundary.
12. Before a public cross-platform claim, Windows-native tests and public CI pass; installation,
    Quickstart, limits, security, contribution, and release evidence are publicly reproducible.

Public commit, push, tag, Release, repository rename, promotion, plugin submission, or programme
application still requires separate maintainer authorization even after these gates pass.

## Current state

- Locally retained for compatibility: stable CLI/evidence core and legacy entry points. The current product layer is the thin Astra Skill Doctor adaptation plugin with a two-layer boundary,
  three answer depths, plain-language eight-field reports, fast first takeover, six lifecycle
  routes, distinct daily/weekly templates, strict-evidence escalation, bounded resource discovery,
  and feedback-driven improvement routing.
- Current local gate: pass the complete source and distribution suite, refresh the local plugin,
  and repeat fresh Codex dogfood for takeover, answer depth, progress, daily, and weekly behavior.
- External release gates: Windows-native tests and public CI, public packaging and documentation,
  and real external adoption evidence.
- Post-v1 ideas: scheduled unattended research, broad forum collection, voice wake-up, and a
  desktop companion. They are not part of the current v1 completion claim.

This contract replaces broader descriptions that implied a database, always-running agent,
automatic memory, or unrestricted autonomous execution.
