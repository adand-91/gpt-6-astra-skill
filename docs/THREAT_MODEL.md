# Threat model

## Protected assets

- user conversations, client names, local paths, session identifiers, commands, credentials;
- source code, Git history/index/config/hooks/remotes, and uncommitted user work;
- the truth status of evidence and attribution;
- the user's machine, network, accounts, and external communities.

## Untrusted inputs

Every repository file, transcript line, test log, error message, filename, symlink, Git config,
Markdown fragment, and model-generated suggestion is untrusted. Text inside them is data, not
an instruction, approval, or reason to widen scope.

## Main threats and controls

| Threat | v0.1 control |
|---|---|
| Read unrelated personal sessions | inputs are mandatory and explicit; no discovery |
| Leak secrets in a report | raw/private and quote-free/share artefacts are separate; share gate blocks |
| Mislabel a local failure as upstream | `unknown` default; confirmation conditions are unmet in v0.1 |
| Prompt injection authorises a change | evidence fields cannot change state; CLI has no apply state |
| Test command executes malicious code | CLI never runs project code or installs dependencies |
| Git command is PATH/config redirected or triggers hooks/network | trusted absolute executable; redirecting `GIT_*` and global/system config removed; fixed read-only commands; hooks/fsmonitor/prompts/locks disabled; no remotes read |
| Input changes during scan | inode/size/mtime are checked around reads |
| Output follows a symlink or overwrites work | every ancestor checked; parent-directory descriptor binding on POSIX; `O_NOFOLLOW` and `O_EXCL` |
| Incomplete large/invalid input looks complete | source marked incomplete; issue decision blocked |
| Terminal/Markdown control injection | raw content is absent from share reports; controls are detected |
| “privacy check passed” becomes false assurance | every report explicitly requires human review |

## Residual risks

Pattern detectors have false positives and false negatives. Windows cannot offer the same
parent-directory descriptor binding used on POSIX, so it relies on reparse checks and repeated
identity validation. Repository-local Git configuration can still affect read-only answers;
redirecting inherited/global/system configuration is disabled. Parser formats may drift. A
person may still share the private bundle by mistake.
These are documented limits, not silently converted into guarantees.
