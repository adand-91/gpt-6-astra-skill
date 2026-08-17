---
name: requirement-ledger
description: >-
  Read a finished or half-finished project's own conversation and turn it into three things:
  what the user actually needed as opposed to what they first asked for, what went wrong and
  at which layer, and which repeated work is worth turning into a Skill. Counting is done by
  a script; the model only interprets, and quotes the user verbatim.
  TRIGGER: the user says 总结我的真需求 / 总结一下错误 / 复盘一下 / 我们到底做到哪了 /
  这活儿干完了 / 哪些能自动化 / 优化一下这个 Skill / 生成优化记录, or asks for a
  retrospective, post-mortem, handoff summary, or "what did we actually learn" over a past
  session, a project, or a time window.
  Do NOT use for live requirement clarification during a task, for ordinary development, or
  to write numbers you have not measured.
---

# Requirement ledger

A project's conversation already contains the answers to the questions people ask afterwards:
what did they really want, where did it go wrong, what did we do by hand three times. Nobody
reads it back, so the answers are lost and the same mistake is paid for again.

This skill reads it back. Mechanically first, then interpretively.

## The one rule

**Every number comes from the script. The model never estimates one.**

Counting messages by eye, guessing proportions, or repeating a figure a subagent said out
loud is the failure this skill exists to prevent — a retrospective with invented numbers is
worse than none, because it is quoted later as fact. Details in
[evidence-rules.md](references/evidence-rules.md).

## Step 0 — get the facts

Always before reading anything:

```bash
python3 scripts/scan_transcript.py --engine both --since 7d --format json --out /tmp/facts.json
python3 scripts/scan_transcript.py --engine claude --project myproject   # one project
python3 scripts/scan_transcript.py path/to/session.jsonl                 # one session
```

Reads Claude Code (`~/.claude/projects`), Codex (`~/.codex/sessions`), or a plain-text
transcript. Streams line by line — real sessions reach 250 MB and single lines reach 1.5 M
characters of base64, so nothing is ever loaded whole. Roughly 1 GB per 3 seconds.

What it hands you: real user turns (**not** tool results, which both engines feed back as
user messages), every user message verbatim, course corrections as flagged candidates,
failed tool calls with the tool named, repeated command shapes, and repeated tool sequences.

Add `--no-text` when the output will be shared: it keeps the counts and drops the verbatim
text.

## Step 1 — the real requirement

What the user needed, which is rarely what they opened with. Built from the **corrections**,
not from the first message: every course correction is a place where the delivered thing and
the wanted thing diverged, and the sentence they used to fix it usually names the real
requirement outright.

Each item is labelled, and the labels never merge:

| Label | Means |
|---|---|
| `SAID` | The user's own words, quoted, with a timestamp |
| `INFERRED` | Your reading of what they meant — must stay marked as yours |
| `UNKNOWN` | The transcript does not answer it; say so instead of filling it in |

Method, and how to walk back to the earliest requirement rather than the most recent:
[real-requirement.md](references/real-requirement.md).

## Step 2 — the mistakes

Not a list of error messages. Each entry gets a layer, because the layer decides whether
anything can be fixed at all: a missing rule, a rule that existed but did not fire, two
rules that conflicted, a wrong-place rule, a genuine tool limit, or a one-off.

Only the first four are worth acting on. Calling a tool limit a process failure produces
rules that cannot work. See [mistakes.md](references/mistakes.md).

## Step 3 — the automatable part

The script's `repeated_commands` and `repeated_tool_sequences` are the raw candidates: work
done by hand three or more times. Most of them should not become a Skill. The test is whether
the *judgement* is stable, not whether the keystrokes repeat —
[skill-extraction.md](references/skill-extraction.md) has the filter, the proposal format,
and what an optimisation record must record.

## Authorisation

Default output is a **proposal plus an optimisation record**. Nothing is written to a real
Skill directory, no production file is edited, no rule is changed.

On explicit go — "开干", "执行", "写吧", "apply it" — generate the actual `SKILL.md`, and
first check the target: reuse or extend an existing Skill before adding a new one. Two Skills
that cover the same ground are worse than the manual work they replaced.

## Output

Both files are written to disk before you summarise anything in chat, because a chat summary
does not survive a context reset:

- the retrospective, from [templates/retro-report.md](templates/retro-report.md);
- the optimisation record, from
  [templates/optimization-record.md](templates/optimization-record.md), if step 3 produced
  anything.

Then check it mechanically:

```bash
python3 scripts/check_retro_report.py path/to/report.md
```

`VALID_RETRO` means the required sections exist, every claim carries a label, and no number
appears without a source. It checks form, not truth.

Failure modes worth knowing before you start:
[anti-patterns.md](references/anti-patterns.md).
