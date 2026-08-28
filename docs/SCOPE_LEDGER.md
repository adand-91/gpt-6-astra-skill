# Scope ledger for the v0.1 build

## Confirmed requirements

- Optimise arbitrary open-source projects, not only AI projects.
- Use Codex interaction context, errors, Git state, and test evidence to expose problems.
- Separate common/upstream problems from project-local and personal problems; preserve unknown.
- Close a loop from evidence to repair proposal and validation.
- Improve work efficiency, simplify operation, and reduce mistakes.
- Preserve the existing Requirement Ledger work instead of starting an unrelated repository.
- Build a credible, maintainable open-source project rather than a rough draft.
- Publish `v0.1.0` only after all release gates pass. Later batches must be backed by real use;
  do not backdate, create empty commits, or split one change into meaningless releases.

## Engineering inferences adopted for v0.1

- “BUG version” means a release organised around real failure evidence and feedback, not an
  intentionally broken build.
- Codex remains the semantic developer; the zero-dependency CLI is an evidence and safety
  substrate, not a replacement for a coding model.
- “Automatically captures context” is constrained to the current task or files the user or
  host explicitly supplies. Silent home-directory discovery would violate the privacy goal.
- “Fixes the program” means a reviewed proposal and host-owned isolated intervention in v0.1.
  Autonomous application is deferred until isolation, approvals, and rollback are proven.

## Deferred or blocked

- Real patch application and arbitrary test execution: blocked on isolation/rollback design.
- Automatic upstream Issue/PR and programme application: not authorised. The maintainer has
  authorised this project's gated `v0.1.0` tag, push, and GitHub Release as visible actions.
- Daily/weekly background automation, GUI, cloud, and multi-user service: deferred.
- Guaranteed external-programme eligibility: outside this project's control.

## Acceptance evidence

- all legacy and v0.1 tests pass;
- editable/wheel install and console entry point work in a clean temporary environment;
- synthetic demo completes offline;
- privacy canary blocks with no output created;
- a real explicit-input scan of this repository completes without changing its Git snapshot;
- translation mirrors and package metadata validate;
- final `HANDOFF.md` is newer than every modified program file and passes its checker.
