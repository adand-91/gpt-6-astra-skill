# Closeout

The closeout is the second half of the ledger's job, and the half that is usually skipped. Its
purpose is a report the user can trust without re-reading the whole conversation.

## Walk back to the beginning

Start from the **earliest** requirement in the task. Not the last few rounds, not what is freshest
in context, not what you happen to have open.

This is the part that fails silently. In a long task, the first three requirements are the ones most
likely to have been overtaken by later work and least likely to be in your recent context. A
closeout that summarises the last two rounds and calls the task finished is the single most common
form of a false "done".

If the ledger is on disk, read it back before writing the report rather than reconstructing it from
memory.

## Settle every item

Each ledger item ends as exactly one of four states. No item may be omitted.

| State | Means | Must also say |
|---|---|---|
| `DONE` | Built, and the acceptance action passes | Where the artifact is |
| `PARTIAL` | Some of it works | What specifically is missing |
| `CANCELLED` | Explicitly dropped by the user | When, and by which decision |
| `BLOCKED` | Cannot proceed | What it is waiting on, and who owns that |

`PARTIAL` and `BLOCKED` are not failures to hide. They are the information the user needs most, and
burying them is what makes the whole report untrustworthy.

## What is not DONE

- A process was started.
- An agent or subtask was spawned.
- A plan, design, or scaffold was written.
- The code compiles but the acceptance action was never run.
- It works in your environment and the sheet named a different one.

If the acceptance action from the sheet was not performed, the item is `PARTIAL` at best, and the
report says which acceptance action was not run.

## Verify against disk, not against the transcript

Before reporting `DONE`, check the actual artifact: the file exists at the stated path, the command
exits zero, the output matches what the sheet promised. Earlier conversation saying "finished" is a
claim, not evidence. Where the transcript and the filesystem disagree, the filesystem wins and the
difference gets reported.

## Report shape

Group by item, not chronologically. A closeout is not a diary.

1. What was asked for originally, and what was added later.
2. Decisions that were superseded or cancelled, and by what.
3. Artifacts that exist, with paths, and how each was verified.
4. `PARTIAL` / `BLOCKED` items with the specific gap.
5. Unresolved conflicts — between docs, versions, or the sheet and reality.
6. The single next action.

Merge related items, keep it short, and do not re-narrate the conversation. The test is whether
someone who read none of the task can act on the report.

## Handoff

If the work continues in another session, agent, or engine, the closeout *is* the handoff document.
Write it to disk before summarising it in chat. A chat summary does not survive a context reset; a
file does.
