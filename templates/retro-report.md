---
window: 2026-08-10T08:00:00+08:00 .. 2026-08-17T08:00:00+08:00
scope: myproject
engines: claude, codex
facts: /tmp/facts.json
---

# Retrospective — myproject

<!-- Every claim carries SAID / INFERRED / UNKNOWN. Every number carries (facts) or a path. -->
<!-- Validate: python3 scripts/check_retro_report.py this-file.md -->

## Measured

<!-- Straight from the scanner. Do not retype, do not round, do not add. -->

- sessions 23, user turns 116, assistant turns 1705 (facts)
- tool calls 785, failed 20 (facts)
- corrections flagged 17, judged real 9 (facts)
- bytes 22,656,379 across 23 sessions (facts)

## Real requirement

**Standing goal** — one sentence on what the whole thing was for. `INFERRED` from the
corrections below.

- 「不是让你重写 我就想让它别每次都问我一遍」 — 2026-08-14T21:12+08:00 `SAID`
- The acceptance test was never stated. `UNKNOWN` — only the user can answer.

**Said three or more times** (the highest-value entries — a thing repeated is a thing never
fixed):

- 「又得我提醒你」×3, 08-12 / 08-14 / 08-16 `SAID`

## Requirement trail

<!-- From the FIRST user message forward, not from the most recent work. -->

| # | Requirement | Ended as | Evidence |
|---|---|---|---|
| 1 | … | `DONE` | path to the artifact |
| 2 | … | `PARTIAL` | what specifically is missing |
| 3 | … | `SILENTLY DROPPED` | never mentioned again after 08-11 |

## Mistakes

| Cost | What happened | Layer | Fix |
|---|---|---|---|
| 20 turns (facts) | Wrong output format assumed, never flagged | `NO RULE` | … |
| 4 turns (facts) | Rule existed in a file read too late | `WRONG PLACE` | Move it |
| 0 | Network flake | `ONE-OFF` | None — do not write a rule |

**Paid for by the user**: the user had to repeat themselves 3 times, and caught one item
reported as done that was not. `SAID`

## Automation candidates

| Repeats | Pattern | Verdict | Why |
|---|---|---|---|
| 13x (facts) | `python3 assemble_final_v2.py` after every edit | script, not Skill | no judgement involved |
| 3x (facts) | 「又得我提醒你」 on the same topic | Skill edit | trigger vocabulary is in the quotes |
| 48x (facts) | `Bash → Bash → Bash` | none | shape of the work, not a workflow |

## Not done / unknown

- … `UNKNOWN` — who could answer it.

## Next single action

One action. Not a list.
