# The confirmation sheet

One screen. Fixed fields. No prose, no hedging, no filler. Its only job is to be *disagreed with* —
if it is too long to read, it cannot do that job.

Copy [templates/confirmation-sheet.md](../templates/confirmation-sheet.md).

## Required fields

| Field | Holds | Fails when |
|---|---|---|
| **Goal** | One sentence on what the user gets and why | It restates the request without naming the outcome |
| **In scope** | The deliverables, itemised | Items are verbs without objects ("improve performance") |
| **Out of scope** | What you are deliberately not doing | Left empty — this is where scope creep enters |
| **Inputs** | Real files, paths, samples, credentials, access | It names a file that does not exist on disk yet |
| **Outputs** | Artifacts and where they land | It says "a report" without a format or a path |
| **Acceptance** | The action the user takes to check it | It is a quality adjective instead of an action |
| **Constraints** | Deadline, budget, platform, permissions, do-not-touch | Unstated limits surface at delivery |
| **Where it runs** | Machine, OS, runtime, account | Assumed to be your own environment |
| **Open items** | Every remaining `OPEN`, and who owes the answer | Emptied to look finished |

Every line carries its label: `CONFIRMED`, `INFERRED`, or `OPEN`.

## Labelling rules

- `CONFIRMED` requires a user statement you can point at. Your own clean restatement is not a
  confirmation until they approve it.
- `INFERRED` is a real commitment, not a hedge — say what you chose, not that a choice exists.
  "Output as CSV (`INFERRED` — say the word if you want xlsx)" is right. "Output format TBD" is not.
- `OPEN` items name who owes the answer. An `OPEN` item with no owner never gets resolved.
- Never split one item across two labels to look more certain. The checker rejects this.
- English labels are written uppercase, and only uppercase counts. Otherwise an acceptance line
  like "run X, open Y, see Z" would read as an `OPEN` item. Chinese labels have no such ambiguity.

## Locking

The sheet is locked by one of exactly two things:

1. The user confirms it, in whole or item by item.
2. The user explicitly delegates: "these details are yours". Every `OPEN` item then becomes
   `INFERRED`, stays labelled, and stays visible.

Silence is not a lock. Neither is the user replying to a different part of the message. If you are
unsure whether it was locked, it was not.

## Size

If the sheet does not fit on one screen, the task is either too big for one sheet — split it — or
the sheet is padded. Nine fields, one to four lines each. No preamble, no closing summary.

## Mechanical pre-check

```bash
python3 scripts/check_confirmation_sheet.py path/to/sheet.md
```

Checks: all nine fields present and non-empty, every item labelled, no item labelled twice, no
`INFERRED` item silently promoted between revisions, `Open items` not blank-with-open-items-in-body,
and total size within one screen. Exit `0` prints `VALID_SHEET`.

It reads form only. A sheet can pass every check and still describe the wrong project — that is what
the user's OK is for.
