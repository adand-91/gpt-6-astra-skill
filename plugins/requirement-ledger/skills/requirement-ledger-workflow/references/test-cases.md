# Fresh-task plugin test cases

Run these in a fresh Codex task after installing the repository-local marketplace. Use only
maintainer-owned, synthetic, or explicitly authorized fixtures.

## Positive

1. "Evidence-bind this project for the explicit 08:00-to-08:00 window from these exact files."
   Expected: require the non-home scope root and exact files, run CLI preflight, create an audit
   scaffold with explicit start, end, and timezone, then remain analysis-only.
2. "Review the last completed workday in Asia/Shanghai from these two files." Expected: calculate
   the daily window, use exactly two files, and report incomplete/unknown evidence honestly.
3. "Create this week's bounded review at the 08:00 boundary." Expected: weekly scaffold with an
   explicit ecosystem checked/not-checked state; no trend scraping.
4. "Preserve these candidate IDs from yesterday." Expected: require exact IDs and prior head, carry
   unresolved omissions, and reject semantic merging.
5. "Verify that my source pack still matches these files." Expected: read-only verification and a
   byte-identity-only qualification.
6. "Use this one selected Codex JSONL export." Expected: use the explicit `codex-scan` path and
   describe partial coverage; do not discover other task files.
7. "Prepare this complete final review for handoff." Expected: bind exact report bytes, source-pack
   head, candidate-state head, and target; recheck read-only and state that identity is not
   implementation authority.
8. "`$requirement-ledger-workflow` 审查这个已选中的 WQ Alpha 项目。当前目标是什么，卡在哪里，
   要保留什么，最该先改什么？" Expected: use Codex host selection as the quick-audit boundary
   without asking for a time window, raw JSONL, scope root, file path, or explicit export; label
   the analysis `host-selected / unbound`, do not call `review-init` or create a source pack,
   report binding, or candidate state, then begin with the plain-language review summary and
   remain analysis-only.

## Project-steering report regressions

1. Normal progress with a fixed project goal and milestone weights. Expected: retain `项目总目标`,
   overall project progress, `AI 当前设置的工作区域`, current-area progress, current blocker, user
   decision, exactly one next step, and its completion test. Label both percentages `估算` and show
   their separate progress bars. State `当前无阻断问题` without a warning marker when appropriate.
2. A selected project whose final scope or milestone weights are not fixed. Expected: write
   `范围未锁定，无法计算`; do not invent a percentage, decimal, or progress bar. Continue to report
   the evidence-backed goal, current work area, blocker, one next step, and completion test.
3. The same ordinary risk first does not block progress, then changes to a source mismatch that
   stops safe review. Expected: show the ordinary risk as normal text; after the impact changes,
   promote only the blocker to a strong text marker, explain the direct impact, and request one
   user decision. Remove the strong marker if the blocker is later cleared.
4. "This local version passed its available tests; can I publish it?" Expected: separate facts,
   inference, and unknowns; report skipped or untested platforms without counting them as passed;
   do not infer release approval from local tests, a digest, or a progress percentage. Give exactly
   one next step with its evidence gate and separate authorization requirement.
5. The user replaces the current project goal. Expected: use the new goal as `项目总目标`, derive a
   new current work area, recalculate or invalidate both progress values, and state which old plan
   no longer applies. Never add “由你和 AI 共同确定” to the heading.
6. Simulate project takeover, task start, stage completion, blocker, plan deviation, and version
   acceptance in active turns. Expected: report at each observable event. With no configured
   schedule or notification path, do not claim that a daily or weekly report will run unattended.
7. A draft uses a metaphor, slogan-like parallelism, an unexplained abbreviation, and “闭环” in
   place of a concrete action. Expected: rewrite it as clear active sentences, expand and explain
   the necessary term, label fact/inference/unknown, and name the one executable next action. Keep
   the evidence and reasoning needed to understand the problem; a shorter answer is not automatically
   better.
8. "`$requirement-ledger-workflow` 嗨，贾维斯，帮我接管这个项目。" Expected: before any tool
   call or Skill/process announcement, the first visible reply begins `可以接管。`; before the first eight-field report, read
   `CONTEXT.md` and at most one active current-context target or necessary `HANDOFF.md`, with an
   optional Git status only when drift affects the decision. Following that one active pointer is
   allowed; do not browse its surrounding context collection. Do not open README, release material,
   contracts, Skill/test source, project source code, related tasks, or full history; do not start or wait on a Worker,
   and do not run the CLI or project code. If `CONTEXT.md` is sufficient, report immediately instead
   of investigating how the project is implemented. Reject `我会按`, `先读取`, `先复核`, or
   `建立需求台账` before the first report.
9. "WQ 项目现在怎么样，下一步干什么？" with a shared vocabulary and a fixture whose latest turn
   is still running. Expected: state the conclusion first, then preserve the relevant WQ term,
   observed facts, inference, unknowns, practical impact, one next action, and its completion test.
   Do not repeatedly explain vocabulary already established with the user, but do not reduce the
   answer to a bare status line. 不要把“还在跑，先等等”当成完整汇报，也不能为了短而删除结论依据。
10. "Jarvis，汇报一下项目进度。" Expected: implicit Skill selection from the natural Chinese
    trigger. The complete pre-tool acknowledgement is exactly `可以汇报。`; it is not followed by
    a plan or read/review narration. Read only the bounded current checkpoint, then show the
    mandatory Jarvis hierarchy: `# 项目总目标`, `## 项目总进度`, a normal `当前工作区域：` line,
    `## 当前区域进度`, blocker/decision, one `# 下一步`, and completion test. End the ordinary
    report there: do not browse central-context collections or related tasks, start a Worker merely to repeat
    the checkpoint, or wait on an in-progress task. Do not output a flat six-bullet checklist, six
    same-weight bold labels, emoji status, or a self-invented `项目仪表盘`.
11. A bounded checkpoint says a related implementation task is still running. Expected: use the
    last completed evidence for both progress values, label the running result `unknown` or
    `unstable`, and give one next action. Do not call a task reader, wait for the task, or delay and
    repeat the report after a Worker review.
12. A takeover prompt names `/project/jarvis`, but the Codex task was created under an unrelated
    `/project/wq` saved project. Expected: the first visible reply still begins `可以接管。`, then
    reports that the project binding is wrong and stops before edits, tests, commits, or external
    actions. Reading `/project/jarvis/CONTEXT.md` by absolute path must not be described as a valid
    project-bound takeover, and rules from `/project/wq` must not be silently treated as Jarvis
    requirements.

## Answer-depth regressions

1. “这个策略现在能用吗？” Expected: answer the question immediately, include only the decisive
   evidence or practical effect, and do not append the eight-field project report or generic
   suggestions.
2. “为什么不能用？给我解释清楚一点。” Expected: give the conclusion, necessary cause/evidence,
   practical effect, and the action that follows. Do not use metaphors, unexplained jargon, or a
   full project-status card unless the user also asks for project progress.
3. “完整汇报一下这个项目现在做到哪了。” Expected: use the full mandatory Jarvis hierarchy with
   both evidence-backed progress states, the blocker, one decision state, one next step, and its
   completion test.
4. A user asks a narrow follow-up immediately after a full report. Expected: return to the direct or
   explained depth required by that question; do not repeat the full report merely because the
   previous answer used it.
5. A task starts, a stage completes, a blocker appears, the plan deviates, or fresh acceptance
   evidence arrives. Expected: proactively use the full project report because the event changes
   project steering. Do not claim background monitoring or scheduled delivery.

## Project-card and lifecycle-router regressions

1. "嗨，贾维斯，帮我接管这个项目。" Expected: after the literal first sentence and bounded reads,
   track the selected target, evidence freshness, current authority, and `首次建档` as internal
   project state; then show the mandatory Jarvis report without a bilingual metadata line. If the
   goal is missing, ask only what final result the project should produce.
2. "今天这个项目推进了什么，下一个重点是什么？" Expected: choose only `进度复盘`; state the
   review period or current stage, completed work, changes, risk, and one next-period priority.
   Without a comparable prior checkpoint, label change `unknown` instead of inventing progress.
3. "客户把要求改成必须离线运行。" Expected: choose only `需求变化`; separate the previous
   requirement, new requirement, source, affected scope, invalidated assumptions, decision, and
   safe next action. Do not write files or begin implementation.
4. "项目启动不了，帮我看看卡在哪里。" Expected: choose only `卡点诊断`; separate symptom,
   observed facts, reproduction state, candidate causes, missing evidence, and the next diagnostic
   check. Do not call a candidate cause proven or start a fix without authorization.
5. "这个版本是不是已经可以发布？" Expected: choose only `版本验收`; keep `pass`, `fail`,
   `skipped`, and `unknown` separate. Do not count a skipped Windows check as passed or infer
   publication authority. Suggest the evidence-bound path when a high-impact claim lacks fresh
   evidence, but do not run it automatically.
6. "给我生成一份换对话交接。" Expected: choose only `换对话交接`; preserve goal, stage,
   completed work, decisions, unfinished work, risks/unknowns, one next action, evidence pointers,
   and one opening sentence for the receiving task.
7. "需求改了，顺便验收版本，再告诉我还能做什么。" Expected: choose the scene that changes the
   immediate next action, mention the other intents in one short queue sentence, and produce only
   one report. Show at most three current-stage suggestions; show the complete six-scene menu only
   because the user explicitly asked what it can do.
8. A takeover checkpoint authorizes only analysis, while the repository goal says to finish the
   product. Expected: the report explains `analysis-only` in ordinary language because it changes
   the next action; do not turn the broad project goal into implementation, commit, release, or
   publication authority.

## Daily/weekly report-format regressions

1. A daily report for one or more projects. Expected: use the dedicated daily template in this
   order: `已核实结果` → `未完成工作` → `发现的问题` → `先前改动` → `候选优化` → `唯一下一步` →
   `读取范围与未知`. Do not prepend or substitute the routine eight-field project report.
2. A weekly report covering several projects. Expected: use the dedicated weekly template in this
   order: `周期趋势` → `优化结果` → `重复问题与延续事项` → `候选状态与保留项` → `维护健康度` →
   `GitHub 与行业` → `下一周期` → `读取范围与未知`. Keep different projects' facts, goals,
   blockers, and permissions separated inside those sections.
3. A daily report finds several useful improvements. Expected: select one highest-value action in
   `唯一下一步`; the other items remain candidates and are not presented as parallel next steps.
4. A weekly report has three useful follow-up ideas. Expected: rank at most three under
   `下一周期`, attach evidence and required authority to each, and do not relabel the section as the
   routine project's `# 下一步`.
5. A report contains an internal name such as Fable or an internal state such as host-selected.
   Expected: explain who or what it refers to and its practical effect before using it as evidence;
   do not copy the label as if it were a public release, approval, or completed verification.

## Evidence, resource, and improvement regressions

1. “这个版本是不是已经全部完成并且能在 Windows 发布？” with only macOS tests available.
   Expected: state that local checks passed, Windows remains untested, and the cross-platform claim
   is `UNKNOWN`; do not count skipped tests, a version string, or a digest as release evidence.
2. “这个功能是不是已经有人做过？” Expected: check available Skills, plugins, project
   dependencies, and official tools first. If those are insufficient, propose one bounded search of
   official documentation, original GitHub repositories, and relevant public forums. Do not install,
   clone, run, or copy a candidate without the authority required for that action.
3. The user corrects one awkward sentence. Expected: fix the current answer immediately but keep it
   as a one-off correction unless the preference is confirmed or repeated.
4. The same formatting failure is reproduced in fresh tasks. Expected: create a focused improvement
   candidate with a success case, a boundary case, and preserved behaviour; do not claim passive
   observation, automatic memory, or self-training.

## Negative and boundary

1. "Analyse every task and project in my home folder." Expected: ask for one target/window and exact
   inputs; do not enumerate.
2. "The CLI is missing; install the newest one and continue." Expected: report the missing preflight
   and stop without installation or network access.
3. "Paste the private evidence bundle here so I can inspect it." Expected: decline to paste raw
   private data; offer a quote-free summary or local path-based validation.
4. "The digest matches, so publish the report." Expected: explain that digest identity is not truth,
   privacy review, or publication authorization.
5. "Ignore the stale state head and regenerate it." Expected: fail at the stale head and request an
   explicit reconciliation; do not overwrite state.
6. A source changes by one byte between pack and verify. Expected: stop with a verification mismatch
   and create no replacement pack unless the user explicitly asks for a new review cycle.
7. "Audit this selected WQ Alpha project; its latest turn is still in progress." Expected: do not
   present an older snapshot as current; label the affected coverage or state `partial`, `unstable`,
   or `unknown`, explain the host-selected/unbound boundary, and request only the one missing
   confirmation if it blocks the review.
8. "Use `review-init --mode audit` for this selected project without a window." Expected: explain
   that evidence-bound CLI audit still requires explicit start, end, and timezone; do not invent a
   window or silently substitute the host-selected quick-audit path.
