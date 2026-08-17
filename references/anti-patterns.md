# Anti-patterns

The failure modes this skill exists to prevent. Each one is cheap to fall into and expensive to
discover late.

## 1. Inferred passed off as confirmed

The agent picks a reasonable default, then writes it into the plan as settled fact. Three rounds
later the user discovers the whole thing targets the wrong platform, and the transcript shows nobody
ever said so.

This is the reason for the three labels. A default is fine. An **unlabelled** default is the bug.

> Bad: "The tool will output xlsx."
> Good: "Output as xlsx (`INFERRED` — CSV is one line to change if you'd rather)."

## 2. The questionnaire dump

Twelve questions in one message, most of them answerable from the repo, several using vocabulary the
user does not have. The user answers four, ignores the rest, and now the ledger is worse than before
because it looks complete.

Three questions per round, ranked by consequence. Everything else you decide.

## 3. Interrogation instead of work

The mirror image: asking about things that are cheap to reverse, so nothing gets built. "What should
I name the function" is not a clarification, it is a delay. Apply the cost-to-undo test and decide.

## 4. Silent scope narrowing

The agent hits a hard part, quietly drops it, delivers the rest, and reports success. The user finds
out at acceptance.

Cutting scope is the user's decision, not a coping mechanism. Deliver everything else in full and say
explicitly what you left out and why.

## 5. Silent scope widening

The opposite, and just as bad. The agent notices adjacent problems and fixes them all. Now the diff
is four times the size of the request, the review is expensive, and the actual ask is buried.

Adjacent problems get named, not fixed. Flag them and move on.

## 6. Closeout by recency

The report covers the last two rounds because that is what is in context. Requirements one through
five, agreed at the start, are neither delivered nor mentioned.

Walk back to the earliest requirement. If the ledger is on disk, read it back rather than recalling
it.

## 7. "Done" meaning "started"

A process was launched, a subagent was spawned, a plan was written, the code compiles. None of these
is done. Done means the acceptance action from the sheet was performed and passed.

## 8. Trusting the transcript over the disk

An earlier message says the file was written. The file is not there — the write failed, or a later
step overwrote it, or it went to a temp directory that no longer exists.

Verify artifacts against the filesystem before reporting them. When they disagree, the filesystem
wins and the difference is reported.

## 9. The ledger that stopped tracking reality

Scope changed three rounds ago and the sheet still shows the original plan. It now actively misleads,
and it does so with authority, because a later reader cannot tell it is stale.

Update on change and mark what was superseded, by name and date.

## 10. Clarifying a task that did not need it

A one-line reversible request gets a nine-field confirmation sheet. This is not rigour, it is
friction, and it teaches the user to ignore the sheets that matter.

The gate is whether clarifying measurably reduces the chance of building the wrong thing. For "fix
this typo", it does not.

## 11. Handing the ambiguity back with the jargon attached

"Do you want optimistic or pessimistic locking?" asked of someone who does not write code. The
question is real, the framing makes it unanswerable.

Two or three concrete options, the cost of each in the user's own vocabulary, and a recommendation.

## 12. Treating one approval as standing permission

The user approved one irreversible action, so the agent takes four more of the same kind. Approval is
per action. A locked sheet authorises the *scope*, not every side effect encountered along the way.

## 13. Refuting without offering the alternative

The user's plan will not work, and the agent says so — and stops there. The user now knows less about
what to do than before they asked, and the exchange reads as obstruction.

Say what breaks, why, and the replacement, in one message. The other half of this failure is building
the replacement silently, which is a scope change wearing a helpful face.

## 14. Laundering a misconception into CONFIRMED

The user states something confidently, so it goes in as `CONFIRMED` and everything downstream is built
on it. But `CONFIRMED` only records that they said it — not that it is true, achievable, or good for
them.

This is distinct from anti-pattern 1, which is about the agent's own guesses. This one is about
treating a user's certainty as evidence. Correct it and re-confirm.

## 15. Pricing by how hard it sounds

"Also just match up the names between the two files" arrives as a footnote and is the entire project.
The estimate gets set on the parts that sounded impressive, and the item that will actually consume
the time — and might partly fail — was never surfaced.

Name the real work before estimating, and say the cheap parts are cheap in the same breath.
