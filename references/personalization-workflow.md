# Beginner Skill personalisation workflow

Load this reference when a user wants to make an existing Codex or Claude Skill fit their own
workflow. The user does not need to understand Skill architecture or use Requirement Ledger's
CLI.

## Minimum input

The only required user input is the one target Skill, its exact folder, or a Codex task that
unambiguously identifies it. The user does not have to diagnose the defect, remember a failure,
or explain how the Skill should be implemented.

After binding the target, the host should:

1. inventory the Skill and its directly referenced resources;
2. use [Codex context discovery](codex-context-discovery.md) to find authorised tasks that
   explicitly used or discussed that Skill;
3. recover user-visible corrections, repeated friction, failed outcomes, retained decisions, and
   behaviour that appears to work;
4. build a private context map that records why each included source is related; and
5. propose the first evidence-backed change card without asking the user to perform the analysis.

The current conversation can be evidence when the host is allowed to use it. Ask for one concrete
failure, a behaviour to preserve, or a desired example only when bounded history retrieval is
unavailable, evidence is insufficient, or the missing answer would materially change the result.
Ask one or two short questions at a time. Never ask the user to choose an architecture, schema,
testing framework, or prompt technique.

## Explain before changing

Produce a compact change card:

| Field | Required content |
| --- | --- |
| Problem | The observable behaviour that wastes time, causes errors, or feels wrong |
| Evidence | What the user directly said or what a supplied failure directly proves |
| Likely layer | Shared Skill, this Skill, personal preference, or `unknown` |
| Preserve | Working triggers, outputs, safety boundaries, and user habits that must remain |
| Proposed change | The smallest instruction, reference, script, or test change likely to help |
| Proof | One success case and one boundary/failure case |
| Rollback | How to restore the previous Skill if the result is worse |

Mark interpretation as interpretation. A personal preference does not need to be disguised as a
universal bug; it is a valid personalisation target. A single failure does not prove an upstream
or shared defect.

## Authorisation and implementation

- “Look, explain, audit, or give me a plan” stops after the change card.
- “Fix it, implement it, start, or go ahead” authorises only the described local Skill change.
- Commit, push, publication, marketplace installation, account actions, and maintainer feedback
  remain separate actions.

When implementation is authorised:

1. locate and follow the host's authoritative Skill source and repository instructions;
2. inventory the current triggers, branches, scripts, references, and behaviour to preserve;
3. change the smallest correct layer instead of appending a catch-all rule;
4. validate structure and referenced paths;
5. replay the success case and the boundary case independently;
6. show the user what changed, what improved, and what remains uncertain;
7. retain a rollback path and do not publish private evidence.

Requirement Ledger's packaged CLI remains optional in this conversational path. Use it when the
case spans many conversations, needs a private evidence bundle, or requires digest-bound
before/after records.

## Completion standard

The work is complete only when a non-expert can answer these questions without reading the Skill
source:

- What problem did we fix?
- What useful behaviour did we preserve?
- What changed in my Skill?
- What example now succeeds?
- What is still unknown or not authorised?

Do not call a rewrite successful merely because the Skill became longer, more detailed, or more
forceful.
