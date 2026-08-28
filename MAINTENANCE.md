# Maintenance policy

Requirement Ledger is maintained by evidence, not by activity theatre. Releases represent a
coherent, tested change. The project does not backdate work, manufacture empty commits, or split
one completed change into meaningless versions to look busy.

## Triage rhythm

- Weekly: review new Issues, Discussions, failures, and user corrections; label each as
  `upstream-candidate`, `project-local`, `personal`, `unknown`, documentation, security, or
  feature request. A label is not confirmation.
- Monthly: publish either a real maintenance release or a short public status note explaining
  what was investigated and why no release was needed.
- Quarterly: review the roadmap, supported Python/provider versions, comparable projects,
  contributor experience, privacy boundaries, and adoption evidence.
- Security: privately triage credible reports promptly and release a patch as soon as a verified
  fix and regression test are ready.

Daily private summaries and weekly ecosystem reviews may help the maintainer, but they are not
automatically committed. No-change days should produce no Git noise.

## Version strategy

The project follows Semantic Versioning while it is pre-1.0:

- `0.1.x`: compatible bug, privacy, parser, packaging, and documentation fixes;
- `0.2.0`: structured test adapters, issue grouping, and daily/weekly report outputs;
- `0.3.0`: only after a proven isolation backend, object-bound approvals, frozen-oracle
  execution, drift checks, and rollback fault injection;
- `1.0.0`: stable promised schemas and CLI, a documented migration policy, a reproducible
  maintainer-owned workflow, and every technical release gate passing on one commit. External
  adoption and sustained maintenance remain post-launch evidence, not claims manufactured by a
  fifteen-day engineering sprint.

Security fixes may accelerate this sequence. Feature pressure never weakens a safety gate.

## Batch release plan

### Batch A — `v0.1.0`: installable evidence loop

Package and CLI, explicit-input transcript adapters, read-only Git snapshot, privacy separation,
conservative attribution, repair drafts, external validation comparison, synthetic demo, CI,
community files, bilingual core documentation, and the original retrospective compatibility
entry points.

### Batch B — `v0.1.x`: real-use hardening

Only fixes backed by the first real local uses: provider-format drift, false privacy positives or
negatives, Windows/macOS/Linux packaging findings, error-message clarity, and regression tests.
Coherent discovery and first-use improvements may also ship here when they do not change the v0.1
contract. There is no predetermined number of patch releases.

### Batch C — `v0.2.0`: reporting and adapters

Structured JUnit/pytest/TAP/cargo/Go adapters, issue grouping with human confirmation, daily
improvement report, weekly project/ecosystem review, and opt-in adoption records without default
telemetry.

### Batch D — `v0.3.0`: controlled intervention

Begins only after the safety work in the project gap ledger is proven. No release date is promised
in advance.

## Release gate

Every public version requires:

1. a linked real issue, security need, or coherent milestone;
2. synthetic regression coverage and all legacy/new tests green;
3. clean install, wheel/sdist, console command, compile, and deterministic demo checks;
4. privacy canary and quote/path/session/remote leakage checks;
5. English/Chinese mirror validation for normative documents;
6. updated changelog, known limitations, migration notes when needed, and release notes;
7. final diff and worktree review with no private evidence or build artefacts;
8. a separately authorised tag, push, and GitHub Release.

Passing CI is necessary, not sufficient. A maintainer makes the release decision.

## Evidence of healthy maintenance

Stars, forks, and watches help discovery but do not prove maintenance. Stronger evidence includes:

- response time and resolution quality for real Issues;
- releases tied to reproducible problems and before/after tests;
- repeat users and outside contributors;
- accepted upstream feedback and documented non-fixes;
- transparent security and compatibility decisions;
- a roadmap whose unfinished items remain visible.
