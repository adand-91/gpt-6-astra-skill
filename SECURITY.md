# Security policy

## Scope and safety model

requirement-ledger processes potentially sensitive local evidence. It must not upload
transcripts, send feedback, apply patches, commit, push, create issues, or change global
configuration on its own. Generated feedback is always `DRAFT — NOT SENT`; proposed local
actions remain not applied until separately reviewed and approved by a person.

Automated redaction or detection is a safeguard, not proof that an artifact is safe to share.
Review every artifact before sharing it outside the machine that produced it.

## Reporting a vulnerability

Do **not** open a public issue and do **not** include a real transcript, secret, access token,
cookie, authorization header, private repository URL, customer name, or personal path.

Instead, contact the repository maintainer through the private contact route listed in the
repository profile. Provide a minimal synthetic reproduction, affected version/commit, impact,
and safe steps to reproduce. If no private route is available, open a public issue containing
only a high-level, non-sensitive request for a private contact channel.

## Supported versions

Security fixes are prioritised for the latest released version. Pre-release versions may change
their data format or command-line behaviour before a stable release.
