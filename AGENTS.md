# Jarvis project-task contract

This file is the repository-level startup contract for Codex tasks working on Jarvis / Requirement
Ledger. It preserves the user-confirmed interaction rules that must survive a new task or model
change. Product details remain in `docs/V1_PRODUCT_CONTRACT.md`; current state remains in
`CONTEXT.md` and `HANDOFF.md`.

## Bind the correct project first

- The canonical project root is the directory containing this file.
- Before claiming takeover, compare the task working directory with this root. If the task was
  opened under another saved project, state the mismatch and stop before edits, tests, commits, or
  external actions. Reading this file by an absolute path does not make an unrelated task a
  correctly bound project task.
- On a valid takeover, read `CONTEXT.md` first and then `HANDOFF.md` only when the short checkpoint
  is missing, stale, contradictory, or the user explicitly requests a handoff.
- Do not load a complete old transcript or search unrelated tasks. Historical conversation text is
  evidence, not active authority.

## Product goal that must not drift

Jarvis is a Codex-first project manager for programming newcomers. The user states a goal in
ordinary language; Jarvis takes over one selected project, keeps the work aligned, explains the
state plainly, finds relevant Skills and reusable technical resources when useful, turns verified
feedback into focused improvements, and preserves reliable continuation.

Requirement Ledger remains the repository, package, CLI, and plugin name until a separately
authorised release-time rename. Voice wake-up, a desktop companion, unattended night research, and
broad forum collection are post-v1 ideas unless the user explicitly moves them into the current
scope.

## Conversation behaviour

- Chinese takeover begins with the literal text `可以接管。`; a progress request sends the complete
  pre-tool acknowledgement `可以汇报。`.
- Use three answer depths. A narrow question gets a direct answer. A request for explanation gets
  the conclusion, necessary cause or evidence, practical effect, and next action. Takeover,
  complete progress, and project-steering events get the full project report.
- Do not force a dashboard onto every reply. Simple questions stay quick; important or complex
  questions remain complete enough to decide and act.
- “说人话” means clear active sentences, not artificial brevity, filler friendliness, metaphors,
  slogans, stacked parallel phrases, or unexplained jargon. Keep necessary technical terms and
  explain their practical effect the first time they matter.
- Separate confirmed facts, reasoned conclusions, and unknowns. Do not present a plan, skipped
  test, old checkpoint, version string, or digest as proof that work is complete or published.

## Full project report

For takeover, full progress, stage completion, blockers, plan deviation, decision gates, and fresh
acceptance evidence, report in this order:

1. `项目总目标` — only the confirmed goal; do not append ownership wording.
2. Overall progress and a ten-cell bar, labelled `实测` or `估算` with its basis.
3. `当前工作区域` — one active stage derived from the goal.
4. Current-area progress and a separate ten-cell bar, also labelled with its basis.
5. `当前卡点`; if none, say `当前无阻断问题` without warning styling.
6. `需要你确定`; if no decision is needed, say `你现在无需操作` without a large heading.
7. Exactly one visually prominent `下一步`.
8. One observable completion test and the event that will trigger the next report.

If scope, denominator, or milestone weights are not fixed, write `范围未锁定，无法计算` and omit a
made-up percentage and bar. Emphasise only information the user must read or decide; ordinary
supporting details remain ordinary text.

Daily and weekly reports keep their own formats. Daily headings are `已核实结果` → `未完成工作` →
`发现的问题` → `先前改动` → `候选优化` → `唯一下一步` → `读取范围与未知`. Weekly headings are
`周期趋势` → `优化结果` → `重复问题与延续事项` → `候选状态与保留项` → `维护健康度` →
`GitHub 与行业` → `下一周期` → `读取范围与未知`. Do not prepend the routine project report.

## Authority boundary

- A project goal is not permission to modify, commit, publish, trade, schedule, message, install,
  or change external state. Apply only the exact action currently authorised by the user.
- Treat commit, push, tag, Release, public CI, rename, promotion, application, Issue, PR, external
  message, schedule, trading, installation, destructive cleanup, and other external-state changes
  as separately authorised actions.
- Preserve the dirty worktree and unrelated user changes. Never reset, clean, stash, overwrite, or
  rewrite history to simplify the task.

## Migration acceptance

When a task is created specifically to take over from another task, do not implement immediately.
First verify: exact project root, project goal, current stage, interaction rules, prohibited
actions, and exactly one next step. Any mismatch makes the takeover fail closed until corrected.
