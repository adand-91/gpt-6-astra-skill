# Extracting the real requirement

The opening message is the worst evidence in the transcript. It was written before the user
knew what was possible, what it would cost, or what they would change their mind about. By
the end they know all three, and they told you — in pieces, while correcting you.

## Corrections are the source

Work from `corrections` in the scanner output, not from the first message.

Every course correction marks a divergence between what was being built and what was wanted,
and the sentence used to close that gap usually names the requirement outright:

> 「不是让你重写 我就想让它别每次都问我一遍」

That single line contains the real requirement, the thing that was wrongly inferred, and the
acceptance test. The opening message for that same task said "优化一下这个流程".

Read the corrections in order. Early ones correct the goal; late ones correct the finish. A
goal correction that arrives late is the expensive kind and belongs at the top of the report.

## Walk back to the earliest requirement

Then go the other way. Start from the **first** user message in the window and follow each
requirement forward to see what became of it.

This is the step that gets skipped, because the early requirements are the ones least likely
to be in your context and most likely to have been overtaken. A retrospective that starts
from the most recent work will confidently omit the first three things the user asked for.

For each, record where it ended up:

`DONE` · `PARTIAL` · `CANCELLED` · `BLOCKED` · `SILENTLY DROPPED`

That last one is the finding worth having. `CANCELLED` means the user decided; `SILENTLY
DROPPED` means nobody did, and it is still owed.

## Separate the three kinds of ask

Requirements in a transcript are not all the same weight, and flattening them loses the
point:

- **The standing goal** — what the whole thing is for. Stated once, usually early, rarely
  repeated, and everything else should serve it.
- **The task of the moment** — what to do next. Numerous, short-lived, and mostly irrelevant
  a day later.
- **The recurring irritation** — said more than once, in different words, often as an aside.
  「又得我提醒你」「你怎么老是」. These are the highest-value items in the whole transcript,
  because a thing said three times is a thing that was never fixed.

Count them. Two mentions is a coincidence; three is a requirement the process is failing to
meet, and it belongs in step 3 as an automation candidate.

## Label everything

| Label | Use |
|---|---|
| `SAID` | Quote plus timestamp. Their words, untouched. |
| `INFERRED` | Your reading. Say what it rests on. |
| `UNKNOWN` | The transcript does not answer it. Name who could. |

Do not resolve an `UNKNOWN` by picking the likely option. The value of this document is that a
later reader can tell your reasoning from their instructions.

## What "real" means here

Not deeper, not psychological, not the user's hidden motivation. Do not write "the user really
wanted to feel in control".

Real means: **the requirement that, had it been stated at the start, would have prevented the
corrections that actually happened.** It is testable against the transcript — if adopting your
version of the requirement would not have avoided the observed corrections, it is not the real
one, and you should say what you cannot explain rather than reaching for psychology.
