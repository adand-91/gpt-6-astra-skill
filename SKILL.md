---
name: requirement-ledger
description: >-
  Keep a live requirement ledger for any task big enough to go wrong: restate the goal in your own
  words, label every item CONFIRMED / INFERRED / OPEN and never let an INFERRED item pass as
  CONFIRMED, ask only the one to three questions whose answers would change the deliverable, lock a
  one-screen confirmation sheet before building, and settle every item as DONE / PARTIAL / CANCELLED
  / BLOCKED at closeout.
  TRIGGER: the request is vague, large, or spans several rounds; scope keeps growing; you are about
  to spend real effort on a target you inferred rather than were told; the user asks "is this what
  you meant", "give me a plan first", "what do you still need", "where are we"; a long task is
  wrapping up and you owe an honest account of what was done, cut, or blocked; work is handed off
  between sessions, agents, or engines.
  Do NOT use for single-step reversible requests, for pure Q&A, or as a way to postpone doing the
  work.
---

# Requirement ledger

An agent's most expensive failure is not a bug. It is finishing something nobody asked for, or
reporting "done" on a scope that quietly shrank. This skill keeps one ledger that opens the task and
closes it.

Non-normative background and failure cases: [anti-patterns.md](references/anti-patterns.md).

## The three labels

Every requirement sits in exactly one state, and the label is always visible to the user:

| Label | Means | Who may move it |
|---|---|---|
| `CONFIRMED` | The user said it, or approved your restatement of it | The user only |
| `INFERRED` | Your default, chosen because being wrong is cheap to reverse | You, but it stays labelled |
| `OPEN` | The answer would change deliverable, cost, schedule, or acceptance | Resolved by asking, or deferred on the record |

One hard rule: **an `INFERRED` item is never written as `CONFIRMED`** — not in a summary, not in a
plan, not in a commit message, not in a status line. Everything else here is procedure. This one is
integrity.

## Opening a task

1. **Restate before asking.** One short paragraph: what you believe the goal is, what you believe
   the finished thing looks like. Restating is not agreement — present it as a candidate.
2. **Build the first ledger** from the request, the files, and the repo. Anything already answered
   in the conversation or on disk starts as `CONFIRMED` and is never asked about again.
3. **Ask at most three questions**, ranked by how much the answer changes the outcome. When the user
   cannot answer in your terms, do not hand the jargon back: give two or three concrete options,
   say what each one costs, and name your recommendation. Details in
   [clarify-loop.md](references/clarify-loop.md).
4. **Loop**: small batch → answer → updated ledger → next batch. Never dump a questionnaire.

Read-only investigation, diagnosis, and reversible spikes the user authorised may proceed while
items are still `OPEN`. Irreversible or expensive work may not.

## When not to ask

Asking is not free; an interrogation is its own failure. Apply one test to each `OPEN` item:

> If I guess wrong, what does it cost to undo?

- **Cheap to undo** — decide it, label `INFERRED`, state it in one line, keep going.
- **Expensive to undo** — outward-facing, destructive, hard to reverse, or it changes the price,
  the schedule, or what acceptance means — ask before building.

Do not ask about things you can verify yourself. Do not ask a second time. When the user says "you
decide", every remaining `OPEN` item becomes `INFERRED` and you proceed.

## Locking

Anything beyond a single reversible step gets a confirmation sheet before you build. Fixed fields —
goal, in scope, out of scope, inputs, outputs, acceptance, constraints, where it runs, open items —
one screen, no prose. Template and field rules:
[confirmation-sheet.md](references/confirmation-sheet.md).

The sheet is locked only by an explicit user OK, or an explicit "you decide these". Silence is not
a lock. Mechanical pre-check before you rely on a sheet:

```bash
python3 scripts/check_confirmation_sheet.py path/to/sheet.md
```

`VALID_SHEET` means the required fields exist, nothing is labelled two ways, and no `INFERRED` item
has been promoted. It checks form, not truth, and it does not replace the user's OK.

## After the lock

Every new request is classified out loud before you act on it:

- **`DEFECT`** — the delivered thing does not do what the sheet says. Fix it, no renegotiation.
- **`REFINEMENT`** — inside the locked scope, no new deliverable. Do it, note it.
- **`NEW SCOPE`** — new deliverable, new surface, or new acceptance. Back to the ledger before any
  work: it is `OPEN` until the user confirms it, and it never enters silently.

Rules and the failure this prevents: [change-control.md](references/change-control.md).

## Closing a task

Walk back to the **earliest** requirement in the task, not the last few rounds, and settle every
ledger item as exactly one of:

`DONE` · `PARTIAL` · `CANCELLED` · `BLOCKED`

Nothing may be dropped silently. `PARTIAL` and `BLOCKED` must say what is missing and why.
Starting a process, spawning an agent, or writing a plan is not `DONE`. Full procedure:
[closeout.md](references/closeout.md).

## Where the ledger lives

Keep it in the reply while the task is short. Once the task spans sessions, write it to disk next to
the work — the ledger is the thing a later agent, or the same agent after a context reset, reads
first. If the project already has a handoff or checkpoint file, the ledger goes there rather than
into a second competing file.
