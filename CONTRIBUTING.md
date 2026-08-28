# Contributing

Thanks for helping improve requirement-ledger. This project is local-first: contributors must
keep user conversations, credentials, private remotes, customer data, and absolute home paths
out of issues, pull requests, fixtures, logs, screenshots, and commit messages.

## Before opening a change

- Discuss a substantial design change in an issue first, using only a minimal synthetic example.
- Do not paste a real transcript, API key, cookie, authorization header, private remote URL, or
  customer identifier. Redact a value even when you believe the repository is private.
- Keep fixes narrowly scoped and preserve the project’s explicit-authorisation boundary:
  feedback is `DRAFT — NOT SENT`; local actions are proposals and are not automatically applied,
  committed, pushed, or sent externally.

## Development expectations

- The runtime has no third-party dependencies and supports Python 3.10 through 3.13.
- Add or update a fully synthetic regression fixture for every parser, privacy, classification,
  or output change. Fixtures must not be derived from a real user session.
- Run the relevant unit tests and `python -m compileall` before requesting review. State exactly
  what you ran and what you did not run.
- Keep output deterministic where practical and keep `unknown` when evidence cannot support a
  conclusion. A successful privacy check is not permission to share data.

## Pull requests

Use the pull-request template. Reviewers may request removal of sensitive material, a smaller
reproduction, or a privacy canary before merging. Maintainers retain final decisions on scope,
compatibility, and release timing.
