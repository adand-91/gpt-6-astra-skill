# Scope ledger for the v0.1 build

## Confirmed requirements

- Optimise arbitrary open-source projects, not only AI projects.
- Use Codex interaction context, errors, Git state, and test evidence to expose problems.
- Separate common/upstream problems from project-local and personal problems; preserve unknown.
- Close a loop from evidence to repair proposal and validation.
- Improve work efficiency, simplify operation, and reduce mistakes.
- Preserve the existing Requirement Ledger work instead of starting an unrelated repository.
- Build a credible, maintainable open-source project rather than a rough draft.
- Anchor the next product stage on non-experts personalising an existing Agent Skill from real
  corrections without first learning Vibe Coding, Skill architecture, YAML, or test terminology.
- Preserve working Skill behaviour, explain the proposed change in plain language, and require
  visible authorisation and before/after scenarios for implementation.
- Let the user name a conversation, Skill, Agent, or project instead of diagnosing the problem;
  the Codex host should recover related authorised history and analyse the full relevant record.
- Provide three uses in one project: one-time audit, daily review of the previous workday, and
  weekly review with GitHub or source-bound industry evidence.
- Adapt the first host layer to Codex. Daily and weekly modes may enumerate projects active only in
  their explicit window; one-time audit remains scoped to the named target.
- Publish `v0.1.0` only after all release gates pass. Later batches must be backed by real use;
  do not backdate, create empty commits, or split one change into meaningless releases.

## Engineering inferences adopted for v0.1

- “BUG version” means a release organised around real failure evidence and feedback, not an
  intentionally broken build.
- Codex remains the semantic developer; the zero-dependency CLI is an evidence and safety
  substrate, not a replacement for a coding model.
- In v0.1, “captures context” remains explicit-file only. In v0.2 host modes, naming a target or
  invoking a time window authorises bounded related-context discovery through Codex host tools or
  a scoped adapter; it never authorises unrelated or disk-wide discovery.
- “Fixes the program” means a reviewed proposal and host-owned isolated intervention in v0.1.
  Autonomous application is deferred until isolation, approvals, and rollback are proven.

## Deferred or blocked

- Real patch application and arbitrary test execution: blocked on isolation/rollback design.
- Automatic upstream Issue/PR and programme application: not authorised. The maintainer has
  authorised this project's gated `v0.1.0` tag, push, and GitHub Release as visible actions.
- Creation of actual recurring host schedules, notifications, GUI, cloud, and multi-user service:
  separate from the open-source mode implementation and not authorised in this build.
- A dedicated packaged history-discovery or `skill-review` CLI remains deferred until the
  Codex-first Skill modes have real-use evidence; v0.1.1 remains backward compatible and unchanged.
- Guaranteed external-programme eligibility: outside this project's control.

## Acceptance evidence

- all legacy and v0.1 tests pass;
- editable/wheel install and console entry point work in a clean temporary environment;
- synthetic demo completes offline;
- privacy canary blocks with no output created;
- a real explicit-input scan of this repository completes without changing its Git snapshot;
- translation mirrors and package metadata validate;
- final `HANDOFF.md` is newer than every modified program file and passes its checker.
