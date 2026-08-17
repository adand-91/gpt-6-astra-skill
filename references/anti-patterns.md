# Anti-patterns

How retrospectives go wrong. Several of these produce a document that reads better than an
honest one, which is why they survive.

## 1. Numbers from memory

"We spent most of the session on the build." Nobody measured that. It gets quoted next week as
a fact, and a decision gets made on it.

The scanner reports turns, tool calls, bytes, and repeat counts. Anything it does not report
is unknown. This is the failure the whole skill is built around.

## 2. Reading first, counting second

You read the conversation, form a story, then look for numbers that fit. They are always
findable. Run the script first — the numbers should be able to surprise you.

## 3. Paraphrasing the correction

「不是让你重写 我就想让它别每次都问我一遍」 becomes "user requested workflow
simplification". The real requirement was in the original sentence and is now gone.

Quote verbatim, with a timestamp. Your summary is an interpretation and gets the `INFERRED`
label.

## 4. Treating keyword hits as findings

The scanner flags 「不对」「wrong」「revert」. 「这个不错」 contains 不 and is praise. A
screenshot with no text can be the sharpest correction in the transcript.

Flagged messages are recall candidates. Each one is judged before it enters the ledger.

## 5. Starting from the most recent work

The last two rounds are what is in context, so the report covers them and confidently omits
the first three things the user asked for — which are precisely the ones most likely to have
been silently dropped.

Walk back to the earliest requirement in the window. Read it from the file, not from memory.

## 6. Trusting the transcript over the disk

The conversation says the file was written. It is not there. Verify artifacts before recording
an outcome; where they disagree, the filesystem wins and the difference is reported.

## 7. "Done" meaning "started"

A process was launched, a subagent was spawned, a plan was written, the code compiled. None of
these is done. If the acceptance action was never performed, the item is `PARTIAL` and the
report says which check did not run.

## 8. Inferred presented as said

Your reading of what the user meant, written as though they said it. A later reader cannot
tell your reasoning from their instructions and will act on your guess as if it were an
instruction. This is the one unforgivable error in the document.

## 9. Filling in the unknowns

An `UNKNOWN` gets replaced with the likely option because gaps look like sloppiness. Three
honest unknowns are more useful than no gaps and two inventions. Name who could answer it.

## 10. Confusing "no rule" with "rule did not fire"

Identical from the outcome, opposite fixes. If a rule existed and was ignored, adding another
rule makes it worse. Search for the existing rule by concept before classifying — finding it
changes the whole recommendation.

## 11. Ranking mistakes by how loud they were

The crash has a traceback and cost one turn. The silent wrong assumption has no error message
and cost twenty. An error-message list ranks these exactly backwards.

Rank by measured cost: turns spent recovering, work discarded, whether the user had to
intervene, whether it shipped.

## 12. Blaming the model as an explanation

"The model misunderstood the requirement" restates the symptom. What was missing, ambiguous,
or unreachable at the moment the decision was made? That is the finding.

## 13. Turning every repeat into a Skill

Three occurrences is a trigger to look, not a mandate to build. If the judgement is not
stable, if it already exists, if a script would do it better, or if it will not recur, the
answer is no. "No new Skill" is a normal outcome of a good retrospective.

## 14. A Skill that only wraps a command

It costs context on every load and buys nothing a `Makefile` target would not. What belongs in
a Skill is the judgement around the script: when to run it, what the output means, what to do
when it fails.

## 15. Padding

Twenty entries including every transient warning. The reader skims, and the six real findings
are lost among them. Cut to what changed or should change.

## 16. Changing things and never checking

Rounds of optimisation records with the outcome field never filled in. The rule set grows, no
one knows whether any of it helped, and nothing is ever removed. An empty outcome column after
several rounds is itself the most important finding in the report.
