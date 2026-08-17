# requirement-ledger

An agent skill for the part of the job that happens before and after the code: working out what was
actually asked for, and reporting honestly on what was delivered.

[中文说明](README.zh-CN.md)

## The problem

Coding agents are good at writing code and bad at two things on either side of it.

At the start, they fill gaps silently. An unstated platform, an unstated output format, an unstated
acceptance test — the agent picks something reasonable, writes it into the plan as settled fact, and
three rounds later you discover the whole thing targets the wrong thing. Nobody ever said it. It was
never flagged as a guess.

At the end, they report by recency. A long task's closing summary covers the last two rounds, because
that is what is still in context. The five requirements agreed at the start are neither delivered nor
mentioned. "Done" gets used for a process that was merely started.

Both failures are cheap to prevent and expensive to discover late.

## The three labels

Every requirement carries exactly one visible label:

| Label | Means |
|---|---|
| `CONFIRMED` | The user said it, or approved your restatement of it |
| `INFERRED` | The agent's default, chosen because being wrong is cheap to reverse |
| `OPEN` | The answer would change the deliverable, cost, schedule, or acceptance |

The hard rule is that an `INFERRED` item is never written as `CONFIRMED` — not in a summary, not in a
plan, not in a commit message. Defaults are fine. Unlabelled defaults are the bug.

## What it does

- **Opens** with a restatement, then at most three questions per round, ranked by how much the answer
  changes the outcome. No questionnaire dumps.
- **Decides instead of asking** when being wrong is cheap to undo, and says which choices those were.
- **Handles the user who is not an expert**: proposes options instead of demanding specifications,
  says when their plan will not get them what they want *and* what to do instead, and names which part
  is the real work before estimating. `CONFIRMED` means they said it, not that it is correct.
- **Locks** a one-screen confirmation sheet — goal, in/out of scope, inputs, outputs, acceptance,
  constraints, where it runs, open items — before expensive work starts.
- **Classifies** every later request as `DEFECT`, `REFINEMENT`, or `NEW SCOPE`, out loud, so scope
  cannot grow or shrink silently.
- **Closes** by walking back to the earliest requirement and settling each as `DONE`, `PARTIAL`,
  `CANCELLED`, or `BLOCKED`, verified against the filesystem rather than the transcript.

Fully bilingual: English is normative, Chinese is a checked mirror, and the validator accepts sheets
written in either language.

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

There is nothing runtime-specific here. `SKILL.md` is a self-contained instruction document with a
YAML front-matter trigger; the `references/` files are loaded on demand. Paste `SKILL.md` into a
system prompt, a `CLAUDE.md`, an `AGENTS.md`, or a rules file and it works:

```bash
cat SKILL.md >> AGENTS.md
```

## Scripts

Both are zero-model, zero-dependency, standard library only. They check form, never truth.

```bash
python3 scripts/check_confirmation_sheet.py sheet.md          # VALID_SHEET or findings
python3 scripts/check_confirmation_sheet.py sheet.md --lang zh
python3 scripts/check_confirmation_sheet.py new.md --baseline old.md   # catch silent promotions
```

`--baseline` compares two revisions of a sheet and fails on any item that moved from `INFERRED` to
`CONFIRMED` without a recorded user confirmation. That is the failure mode the labels exist to
prevent, so it is worth catching mechanically.

```bash
python3 scripts/check_translation_sync.py            # TRANSLATIONS_IN_SYNC or drift
python3 scripts/check_translation_sync.py --update   # re-stamp after translating
python3 -m unittest discover -s tests -v             # 37 tests
```

Each `*.zh-CN.md` carries the SHA256 of its English source at translation time, so an edit to the
normative file makes its mirror mechanically detectable as stale instead of quietly wrong.

## Repo layout

```
SKILL.md                  normative skill document (loaded by the agent)
SKILL.zh-CN.md            checked Chinese mirror
references/               loaded on demand: clarify loop, sheet rules, non-expert users,
                          change control, closeout, anti-patterns (15 of them)
                          — each with a .zh-CN.md mirror
templates/                the confirmation sheet, and the nine fields as plain-language
                          questions with example answers — both in English and Chinese
scripts/                  the two checkers
tests/                    unittest, no third-party dependencies
```

## What this is not

- Not a planning framework, a ticket system, or a methodology. One ledger, three labels, nine fields.
- Not a substitute for doing the work. Anti-pattern 3 is specifically about agents that clarify
  instead of building.
- Not applicable to small reversible requests. Applying a nine-field sheet to "fix this typo" is
  friction, and it teaches users to ignore the sheets that matter. Anti-pattern 10.
- Not able to tell you whether a sheet is *true*. The checkers validate structure. Only the user can
  confirm the content.

## License

MIT. See [LICENSE](LICENSE).
