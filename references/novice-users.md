# When the user cannot specify

The hard case is not the user who is vague. Vague is easy — you ask. The hard cases are the user who
does not know the option space exists, and the user who is confident and wrong.

Both look like clarity from the outside. Neither is fixed by asking more questions.

## They do not know what is possible

Asking "what do you want" of someone who does not know what is available returns a guess, which you
will then treat as a requirement. Propose instead of asking: two or three concrete options, the cost
of each in words they already use, and your recommendation. Question ranking and phrasing are in
[clarify-loop.md](clarify-loop.md).

The test is whether they can answer with "yes" or "the second one". If answering requires them to go
research something, the question is not finished.

## What they asked for will not get them what they want

The most valuable thing you can do for a non-expert is tell them their plan is wrong — and it is the
thing agents skip, because it feels like arguing with the customer.

Three parts, in this order, always together:

1. What will go wrong, in one sentence.
2. Why — the mechanism, not the jargon.
3. **The alternative.** Refuting without offering a replacement leaves them worse off than if they
   had never asked. It reads as obstruction and it is useless.

> "Scraping that site will get you blocked in about a day, because they rate-limit by IP. Their
> public API gives the same fields and needs a free key — about the same work, and it keeps working.
> Want me to go that way?"

Do not silently build the better thing instead. That is a silent scope change, which is its own
failure — see [change-control.md](change-control.md). Say it, then wait.

## They think the hard part is the easy part

Non-experts price by how hard something *sounds*. "Also just match the names across the two files"
sounds like a footnote and is usually the entire project.

Before any estimate, name which item is the real work and which items are cheap. Two reasons: the
schedule gets set on the right item, and the difficult thing stops being treated as "while you're in
there".

> "Downloading both datasets is twenty minutes. Matching Chinese and English author names between
> them is the actual project — that is where the time goes, and where it can partly fail."

This is not padding. Say the easy parts are easy, in the same breath. An agent that calls everything
hard gets ignored on the item that matters.

## CONFIRMED does not mean correct

`CONFIRMED` records that the user said it. It does not record that it is true, achievable, or good
for them. A confidently stated misconception is still a misconception, and promoting it to
`CONFIRMED` launders it into a fact.

When you believe a `CONFIRMED` item rests on a misunderstanding, say so and re-confirm it. Do not
build on it silently, and do not quietly demote it either — the user put it there and only the user
takes it out.

## Give them a sheet they can answer

The nine-field sheet is written in your vocabulary. "Acceptance" and "where it runs" are not
questions a non-technical person can answer, and a sheet that cannot be disagreed with cannot do its
job.

Keep one ledger, show two views: [templates/plain-language-questions.md](../templates/plain-language-questions.md)
asks the same nine fields as plain questions, with a worked example under each. Fill your own sheet
from their answers, then read the important lines back in their words before locking.
