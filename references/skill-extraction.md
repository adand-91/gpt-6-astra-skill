# Turning the repeats into a Skill

The scanner's `repeated_commands` and `repeated_tool_sequences` list work that was done by
hand three or more times. Most of it should not become a Skill.

## The filter

Repetition is the trigger, not the justification. Four questions, in order — the first `no`
ends it:

1. **Is the judgement stable?** Was the decision the same each time, or did it depend on
   context that changes? `python3 build.py && pytest -q` is stable. "Pick the right chart for
   this data" is not, and a Skill that pretends otherwise will be wrong confidently.
2. **Does it already exist?** Search by concept, not by the words in the transcript. Adjacent
   Skills, a script in the repo, a shell alias, a Makefile target. Two Skills covering the
   same ground are worse than the manual work they replace.
3. **Would a script do it better?** If there is no judgement at all, it wants a script, not a
   Skill. A Skill that only says "run this command" costs context on every load and buys
   nothing over a `Makefile`.
4. **Will it recur?** Three times in one project that is now finished is history, not a
   pattern. Three times across three projects is a pattern.

What survives all four is usually **the judgement around a script**, not the script and not
the prose: when to run it, what the output means, what to do when it fails.

## What the repeats are actually telling you

Read the shape, not just the count.

- **Same command, many times, same session** — usually a missing loop or a broken feedback
  cycle, not a Skill. Ask why it had to run fourteen times.
- **Same command, across sessions and projects** — a genuine candidate.
- **A repeated tool *sequence*** (`Write → Bash → Read`) — the workflow shape. If a fixed
  sequence occurs constantly, the Skill is the order and the checks between steps, which is
  exactly the thing prose is good at and a script is not.
- **Repeated corrections on the same topic** (from step 1) — the strongest candidate of all,
  and the one no command counter finds. The user having to say the same thing three times is a
  rule that is missing, unfindable, or being ignored — cross-check the layer from
  [mistakes.md](mistakes.md) before writing anything, because `RULE DID NOT FIRE` means a new
  Skill will be ignored too.

## The proposal

For each survivor, write:

- **Trigger** — the situation in the vocabulary someone would actually use, including the
  words from the transcript. A trigger written in your own coinage never fires.
- **What it does** — the steps, and where judgement enters.
- **What it must not do** — the boundary. Skills without one grow until they collide.
- **Evidence** — the counts from the scanner and the quoted corrections. No evidence, no
  proposal.
- **Layer** — a new Skill, an edit to an existing one, a script, a project rule, or nothing.
  "Nothing" is a legitimate and common outcome; say why.
- **Cost** — what it adds to every load, weighed against the work it removes.

## Authorisation

Default is proposal plus record. Do not create or edit a Skill file, do not touch a rules
file, do not modify anything under a live skills directory.

On explicit go, and only then:

1. Confirm the target — reuse or extend before creating.
2. Write it, keeping the trigger vocabulary from the evidence.
3. Record what changed and why, in the optimisation record.
4. State plainly how it will be known to have worked, and what would show it made things
   worse.

A generated Skill that nobody validated is a liability with a trigger attached. If you cannot
name the check, say so instead of shipping it.

## The optimisation record

One file per round, from
[templates/optimization-record.md](../templates/optimization-record.md). Its job is that the
next round can tell whether the last one helped: what was changed, on what evidence, what was
expected, and — filled in later — what actually happened.

A record with an empty outcome after several rounds is the finding. It means changes are being
made and never evaluated, which is how a rule set grows without getting better.
