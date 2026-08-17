# Change control after the lock

Once a sheet is locked, the ledger stops being a planning document and starts being a contract with
the user. Every new request gets classified out loud *before* you touch anything.

## The three classes

**`DEFECT`** — the delivered thing does not do what the locked sheet says.

Fix it. Do not renegotiate, do not bill it as new work, do not explain why the sheet was ambiguous.
If the sheet genuinely was ambiguous, fix the thing first and tighten the sheet second.

**`REFINEMENT`** — inside the locked scope, no new deliverable, no new acceptance.

Do it and note it in the ledger. Refinements are not free forever: if they keep arriving, say so
plainly with a count, because a stream of small refinements is how a locked scope doubles without
anyone deciding to double it.

**`NEW SCOPE`** — a new deliverable, a new surface, a new platform, or a changed acceptance test.

It enters the ledger as `OPEN`. It does not get built because it was mentioned. Say what it adds,
what it displaces, and what it costs, then wait.

## The distinction that actually matters

Not "how big is it" but **"was this in the locked sheet".**

A five-minute change that adds a new output file is `NEW SCOPE`. A two-day rewrite that makes the
sheet's stated acceptance test pass is a `DEFECT`. Size is a cost estimate, not a class.

## Saying it out loud

Classify in the reply, not silently in your head:

> That is `NEW SCOPE` — the sheet has CSV output only. Adding the xlsx export is about an hour and
> pushes the last item to tomorrow. Want it in, or after?

The user can overrule any classification. That is fine and it is on the record. What is not fine is
absorbing new scope silently, because then the closeout report cannot be honest — you will have work
in the tree that no ledger item explains.

## Re-locking

When new scope is accepted, update the sheet and re-lock the changed lines. Do not keep a mental
list of accepted extras. A ledger that stopped tracking reality three rounds ago is worse than no
ledger, because it still looks authoritative.

Mark what was replaced, explicitly:

> Old plan: single CSV. Superseded by 2026-08-17 decision: CSV + xlsx.

A later agent reading two contradictory plans will guess, and guess wrong. Naming the supersession
is what prevents that.

## Scope reduction is also a change

If you decide something is not worth doing, that is not yours to absorb either. Narrowing the
deliverable is a `NEW SCOPE` change in the other direction: propose it, say what is lost, and let
the user decide. Delivering less than the locked sheet and reporting success is the failure this
whole skill exists to prevent.
