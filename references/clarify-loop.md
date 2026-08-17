# The clarify loop

One round is: **small batch → answer → updated ledger → next batch.** Not a questionnaire, not a
single blocking interrogation, not silent guessing.

## Ranking questions

You get at most three per round, so rank by how far the two answers diverge. Ask the question whose
answers lead to *different work*, and skip the one whose answers lead to the same work.

Highest value first:

1. **What the finished thing is.** A script, a service, a report, a repo? Wrong answer here voids
   everything downstream.
2. **What counts as done.** The acceptance action — what the user will actually do to check it. An
   unstated acceptance test is the most common cause of "that's not what I wanted".
3. **Where it runs.** Which machine, OS, runtime, account. Cross-platform assumptions are expensive
   and invisible until the end.
4. **What the real input is.** A sample file beats a description of a file. Ask for the sample.
5. **What is explicitly out.** The cheapest question in the list and the one most often skipped.
6. **Hard limits.** Deadline, budget, permissions, things you may not touch.

Below that line — naming, formatting, library choice, internal structure — do not ask. Decide,
label `INFERRED`, move on.

## When the user cannot answer in your terms

They are not required to be a product manager. If a question needs vocabulary they do not have, the
question is yours to fix, not theirs to research.

Do not do this:

> What retention policy do you want on the intermediate artifacts?

Do this:

> Old runs: keep everything (disk grows, easy to debug), keep the last 10 (my recommendation), or
> delete after each run (smallest, no history)?

Rules: name two or three concrete options, say what each costs in words the user already uses, and
recommend one. A question with a recommendation attached can be answered with "yes".

## Do not re-ask

Before asking, check the conversation, the files, and the repo. Anything already answered there is
`CONFIRMED` and asking again reads as not having looked. This includes things the user answered
several rounds ago and things visible in the code.

## While items are still OPEN

Allowed: reading, searching, diagnosing, measuring, drafting, and any reversible spike the user
authorised. Do the entire part of the work that does not depend on the open answer, then ask.

Not allowed: irreversible or outward-facing actions, and anything whose cost you would not want to
throw away if the answer comes back the other way.

## Ending the loop

Stop asking when every remaining unknown is cheap to reverse. That is the point of "enough
clarity" — not zero questions. Two rounds is normal. Four rounds on a small task means you are
asking about things you should be deciding.
