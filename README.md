# requirement-ledger

An agent skill that reads a project's own conversation back and tells you three things: what
the user actually needed, what went wrong and at which layer, and which repeated work is worth
turning into a Skill.

[中文说明](README.zh-CN.md)

## The problem

The answers to the questions people ask after a project are already in its transcript. Nobody
reads it back, so they are lost and the same mistake gets paid for twice.

Ask an agent to summarise it and you get something worse than nothing: numbers estimated by
eye, the opening request treated as the requirement, a list of error messages ranked by how
loud they were, and a summary of the last two rounds presented as a summary of the project.
That document then gets quoted as fact.

The transcript can answer all three questions properly, but only if the counting is mechanical
and the quoting is verbatim.

## How it works

**Step 0 is a script, always.** `scan_transcript.py` reads Claude Code, Codex, or a plain-text
transcript and reports what must not be guessed: real user turns, every user message verbatim,
course corrections, failed tool calls, repeated command shapes, repeated tool sequences. Then
the model interprets — and may not produce a number the script did not.

**Step 1 — the real requirement.** Built from the corrections, not the first message. Every
correction marks where the delivered thing diverged from the wanted thing, and the sentence
used to fix it usually names the requirement outright. Then it walks back to the *earliest*
requirement and records what became of each: done, partial, cancelled, blocked, or silently
dropped.

**Step 2 — the mistakes.** Each one gets a layer, because the layer decides whether a fix is
possible at all: no rule, rule did not fire, rules conflicted, wrong place, tool limit, one-off.
Only the first four are actionable, and confusing the first two produces rules that cannot work.

**Step 3 — the automatable part.** Repeated work is the trigger to look, not a mandate to
build. The test is whether the *judgement* is stable, not whether the keystrokes repeat. "No new
Skill" is a normal outcome.

Three labels run through all of it and never merge: `SAID` (their words, quoted, timestamped),
`INFERRED` (your reading, marked as yours), `UNKNOWN` (the transcript does not answer it — say
so instead of filling it in).

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

`SKILL.md` is a self-contained instruction document; the `references/` files load on demand and
the scripts are plain Python. Paste it into a system prompt, a `CLAUDE.md`, an `AGENTS.md`, or a
rules file:

```bash
cat SKILL.md >> AGENTS.md
```

## The scanner

Zero dependencies, standard library only.

```bash
python3 scripts/scan_transcript.py --engine both --since 7d
python3 scripts/scan_transcript.py --engine claude --project myproject --format json --out facts.json
python3 scripts/scan_transcript.py path/to/session.jsonl
python3 scripts/scan_transcript.py --engine both --since 7d --no-text   # share-safe
```

Real transcripts are hostile, and the scanner is built around that rather than around the happy
path:

- Sessions reach 250 MB and single lines reach 1.5 M characters of base64. It streams line by
  line, measures oversized lines instead of parsing them, and never decodes base64. About 1 GB
  in 3 seconds; `--since` skips stale files by mtime first.
- **Both engines feed tool output back as user messages.** Counting those inflates a 79-turn
  conversation into 918 "user turns" and poisons the requirement extraction with tool logs. The
  Claude adapter excludes `tool_result` blocks; the Codex adapter prefers
  `event_msg/user_message`, which is the actual typed input.
- Claude Code names its directories after a slugified cwd, which turns every non-ASCII character
  into a dash — a project called `接单工作台` lives in `-Users-…-Desktop------` and can only be
  found through the cwd recorded inside each file. `--project` matches both.
- Course corrections are keyword recall, so they are reported as **candidates**. 「这个不错」
  contains 不 and is praise. The model judges each one.

## Checking the output

```bash
python3 scripts/check_retro_report.py report.md          # VALID_RETRO or findings
python3 scripts/check_retro_report.py report.md --lang zh
python3 scripts/check_translation_sync.py                # zh mirrors not stale
python3 -m unittest discover -s tests -v                 # 56 tests
```

`check_retro_report.py` rejects the failures that make a retrospective actively harmful: a
number with no source, a claim with no label, a missing window or a window with no UTC offset,
a vague quantity word standing in for a measurement, a section padded to look complete. It
checks form, not truth. English and Chinese section names and labels are both recognised.

## Repo layout

```
SKILL.md                  normative skill document (loaded by the agent)
SKILL.zh-CN.md            checked Chinese mirror
references/               evidence rules, real-requirement extraction, mistake layers,
                          skill extraction, 16 anti-patterns — each with a .zh-CN.md mirror
templates/                retrospective report and optimisation record, EN and 中文
scripts/                  scan_transcript.py (the mechanical layer),
                          check_retro_report.py, check_translation_sync.py
tests/                    unittest, no third-party dependencies
```

Each `*.zh-CN.md` carries the SHA256 of its English source, so editing the normative file makes
its mirror mechanically detectable as stale rather than quietly wrong.

## What this is not

- Not live requirement clarification. This runs backwards over work that already happened.
- Not a dashboard or a metrics tool. The counts exist to keep the prose honest.
- Not able to judge whether a report is *true*. The checker validates structure; only the
  people who were there can confirm the content.
- Not a Skill generator you should leave unattended. It proposes; it writes a real `SKILL.md`
  only on an explicit go, and an unvalidated generated Skill is a liability with a trigger
  attached.

## Privacy

The scanner reads your local transcripts and its output contains verbatim user text by design —
that text is the evidence. Nothing is uploaded. Use `--no-text` for any output you intend to
share, paste, or attach: it keeps every count and drops the quotes.

## License

MIT. See [LICENSE](LICENSE).
