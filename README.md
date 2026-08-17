# requirement-ledger

**From vibe coding to knowing what you actually wanted.** Point it at a project you already
built with an AI agent and it reads the conversation back: what you really needed, what went
wrong, and which repeated work is worth turning into a Skill.

[中文说明](README.zh-CN.md)

## Who this is for

You built something by talking to an agent. It mostly works. You could not have written a
spec for it before you started, and you still could not write one now.

That is not a discipline problem. Nobody can specify a thing they have not seen yet. But it
has a real cost: the agent filled every gap you left silently, some of those guesses were
wrong, you spent a dozen rounds correcting them, and none of it was written down. Next project,
same gaps, same dozen rounds.

If you are a product manager with a signed-off requirements document, you do not need this.

## You do not have to know what you want

Skip the spec. Build the thing badly, then let this read your own words back to you.

Here is the trick it is built on. Every time you told the agent it got something wrong, you
described what you actually wanted — precisely, in your own vocabulary, without meaning to:

> 「不是让你重写 我就想让它别每次都问我一遍」

That one sentence contains the real requirement, the wrong guess the agent made, and how you
would test it. The message you *opened* that task with was 「优化一下这个流程」.

So the requirement is not extracted from what you asked for. It is extracted from **where you
had to correct it** — which is the one place in the transcript where you were specific.

## How it works

Three things you can ask for, in plain words: 总结我的真需求 · 总结一下错误 · 哪些能自动化.

**Step 0 always runs a script.** Ask an agent to "summarise the project" and you get numbers
guessed by eye, the opening message treated as the requirement, and a summary of the last two
rounds passed off as a summary of the whole thing. So the counting is mechanical:
`scan_transcript.py` reads the raw session files and reports real user turns, every message you
typed verbatim, your course corrections, failed tool calls, and repeated commands. The model
interprets — and may not state a number the script did not produce.

**Step 1 — what you actually needed.** Built from the corrections, as above. Then it walks back
to the *earliest* thing you asked for and follows each one forward, because the requirements
most likely to have been quietly abandoned are the ones from the first day. Each ends as done,
partial, cancelled, blocked, or **silently dropped** — that last one is the finding worth
having, and it is still owed to you.

**Step 2 — what went wrong, and whether it is fixable.** Not a list of error messages. Each
mistake gets a layer: no rule existed, a rule existed and did not fire, two rules conflicted,
a rule sat somewhere read too late, a genuine tool limit, or a one-off. Only the first four can
be acted on, and mixing up the first two is why "just add another rule" usually makes things
worse.

**Step 3 — turn the repeated work into a Skill.** You ran the same command by hand fourteen
times; the script noticed. Most repeats should *not* become a Skill, so there is a filter: is
the judgement stable, does it already exist, would a plain script do it better, will it happen
again. What survives gets written as a proposal. It only becomes a real `SKILL.md` when you say
go — an unreviewed generated Skill is a liability with a trigger attached.

Three labels run through all of it and never merge: `SAID` (your words, quoted, timestamped),
`INFERRED` (the model's reading, marked as the model's), `UNKNOWN` (the transcript does not
answer it — so it says so instead of filling it in).

## Install

### Claude Code

```bash
git clone https://github.com/adand-91/requirement-ledger ~/.claude/skills/requirement-ledger
```

### Codex

```bash
git clone https://github.com/adand-91/requirement-ledger ~/.codex/skills/requirement-ledger
```

### Any other agent

`SKILL.md` is a self-contained instruction file, the `references/` load on demand, and the
scripts are plain Python with no dependencies. Paste it into a system prompt, a `CLAUDE.md`, an
`AGENTS.md`, or any rules file:

```bash
cat SKILL.md >> AGENTS.md
```

Then just talk to your agent normally: 复盘一下这个项目 / 总结我的真需求 / 哪些能自动化.

## The scanner

Zero dependencies, standard library only. It can also be run on its own.

```bash
python3 scripts/scan_transcript.py --engine both --since 7d
python3 scripts/scan_transcript.py --engine claude --project myproject --out facts.json
python3 scripts/scan_transcript.py path/to/session.jsonl
python3 scripts/scan_transcript.py --engine both --since 7d --no-text   # share-safe
```

Real transcripts are hostile, and it is built around that rather than the happy path. Each of
these cost a wrong number before it was understood:

- Sessions reach 250 MB and single lines reach 1.5 M characters of base64. It streams line by
  line, measures oversized lines instead of parsing them, and never decodes base64. Roughly
  1 GB in 3 seconds; `--since` skips stale files by mtime before opening them.
- **Both engines feed tool output back as user messages.** Counting those turns a 79-turn
  conversation into 918 "user turns" and floods the requirement extraction with tool logs —
  measured on a real 105 MB session. The Claude adapter drops `tool_result` blocks; the Codex
  adapter prefers `event_msg/user_message`, which is what you actually typed.
- Claude Code names its folders after a slugified working directory, so every non-ASCII
  character becomes a dash and a project called `接单工作台` lives in `-Users-…-Desktop------`.
  Matching on the path alone returns zero sessions; `--project` matches the path *or* the
  working directory recorded inside each file.
- Corrections are found by keyword, so they are reported as **candidates**, never findings.
  「这个不错」 contains 不 and is praise. A screenshot with no words can be the sharpest
  correction in the transcript. The model judges each one.

## Checking the output

```bash
python3 scripts/check_retro_report.py report.md          # VALID_RETRO, or what is wrong
python3 scripts/check_retro_report.py report.md --lang zh
python3 scripts/check_translation_sync.py                # Chinese mirrors not stale
python3 -m unittest discover -s tests                    # 56 tests
```

The report checker refuses the things that make a retrospective actively harmful, because it
will be quoted later as fact: a number with no source, a claim with no label, a missing time
window or one with no UTC offset, a vague quantity word standing in for a measurement, a
section padded out to look complete. It checks form, not truth. English and Chinese section
names and labels are both recognised.

## What's inside

```
SKILL.md                  the skill itself, ~100 lines, loaded by the agent
references/               5 docs loaded on demand: evidence rules, real-requirement
                          extraction, mistake layers, skill extraction, 16 anti-patterns
templates/                retrospective report, optimisation record
scripts/                  scan_transcript.py — Claude Code, Codex and plain-text adapters
                          check_retro_report.py, check_translation_sync.py
tests/                    56 tests, no third-party dependencies
```

Everything exists twice, in English and Chinese. English is normative; each `*.zh-CN.md` carries
the SHA256 of its English source, so editing the normative file makes its mirror mechanically
detectable as stale rather than quietly wrong.

## What this is not

- **Not a spec writer.** It does not help you decide what to build. It tells you what you
  already asked for, once there is a transcript to read.
- **Not a dashboard.** The counts exist to keep the prose honest, not to be looked at.
- **Not able to tell you a report is _true_.** The checker validates structure. Only the people
  who were there can confirm the content.
- **Not an unattended Skill factory.** It proposes; it writes a real `SKILL.md` only on an
  explicit go, and "no new Skill" is a normal, common outcome.

## Privacy

The scanner reads your local session files and its output contains your messages verbatim by
design — those quotes are the evidence. Nothing is uploaded anywhere. Use `--no-text` for any
output you plan to share, paste, or attach: it keeps every count and drops every quote.

## License

MIT. See [LICENSE](LICENSE).
