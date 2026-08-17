# Extracting the mistakes

A list of error messages is not a retrospective. The scanner already produced that list; the
work is deciding which entries mean anything and at which layer they can be fixed.

## Layer first

Every mistake gets exactly one layer. The layer decides whether a fix is even possible, and
mislabelling it produces rules that cannot work.

| Layer | Means | Fixable by |
|---|---|---|
| `NO RULE` | Nothing anywhere said to do it differently | Writing the rule |
| `RULE DID NOT FIRE` | The rule existed and was not applied | Trigger, placement, or wording — **not** a new rule |
| `RULES CONFLICTED` | Two sources said different things | Deciding which one wins, and deleting the other |
| `WRONG PLACE` | The rule exists somewhere it is not read in time | Moving it |
| `TOOL LIMIT` | The environment cannot do it | Nothing. Document and route around |
| `ONE-OFF` | Noise, a flake, an external outage | Nothing. Do not sediment it |

The first four are worth acting on. The last two are worth recording precisely so nobody
writes a rule against them next quarter.

## The distinction that matters most

`NO RULE` versus `RULE DID NOT FIRE`.

They look identical from the outcome and have opposite fixes. If a rule existed and was
ignored, **adding another rule makes it worse** — you now have two rules with the same
trigger problem and more context spent. The fix is why it did not fire: the trigger did not
match the situation's vocabulary, the rule sat in a file that is only read later, it was
buried in paragraph nine, or it contradicted something more prominent.

Check before you classify. Search for the rule by concept, not by the words the user just
used. Finding it changes the entire recommendation.

## Cost, not severity

Rank by what it actually cost, measured from the transcript:

- turns spent recovering (count them from the scanner output)
- work thrown away
- whether the user had to notice and intervene
- whether it shipped

A crash that was fixed in the next turn cost almost nothing. A silent wrong assumption that
survived twenty turns cost the twenty turns. **The expensive mistakes are usually the quiet
ones**, which is exactly why an error-message list ranks them wrong — the loud failure has a
traceback and the costly one does not.

The most expensive class has no error message at all: work that completed successfully and
was not what was wanted.

## Mistakes the user paid for

Give these their own section, from `corrections`:

- the user had to say the same thing twice or more
- the user caught something the agent claimed was done
- the user had to supply information they had already supplied
- the user had to ask "did you actually check"

These are process failures whether or not anything errored, and they are the entries most
likely to convert into a Skill change in step 3.

## Do not

- **Do not pad.** Six real entries beat twenty with fillers. A retrospective that lists every
  transient warning trains its reader to skim.
- **Do not write per-mistake apologies.** Record the fact, the layer, the cost, the fix.
- **Do not blame the model as an explanation.** "The model misunderstood" is a restatement of
  the symptom. Name what was missing, ambiguous, or unreachable at the moment of the decision.
- **Do not turn a `TOOL LIMIT` into a discipline problem.** No amount of instruction fixes a
  sandbox that cannot reach the network.
