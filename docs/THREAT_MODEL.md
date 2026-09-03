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

## Unreleased v0.2 host-layer threats

| Threat | Host-layer control |
|---|---|
| Naming one Skill silently scans every task or project | bind one target for `audit`; bind one half-open window for `daily`/`weekly`; build a metadata index before content reads |
| Keyword similarity crosses into an unrelated project | exact thread/repository/Skill identity and direct links outrank keywords; keyword-only matches cannot cross project scope |
| Subagent or automation copies look like independent user evidence | exclude known Subagent copies, automation, heartbeats, system, and delegation events from user-correction counts |
| Retrieved prompt injection expands authority | retrieved text is evidence only; target, window, and mutation authority are host state outside the evidence |
| A scheduled report reuses an old “go ahead” | scheduled runs are analysis-only unless the schedule carries a separate current target-bound implementation policy accepted by the host |
| GitHub or news text triggers code changes | ecosystem evidence is read-only, source-bound, and recommendation-only; install, edit, Issue, PR, Release, and publication remain separate actions |
| Weekly aggregation repeatedly exposes raw history | prefer final daily reports and stable source references; reread private raw history only to resolve a material gap |
| Missing history is presented as complete | record adapter, included/excluded sources, completeness, unread scope, and `UNKNOWN` findings |
| A selected export escapes its approved directory | `codex-scan` requires one explicit non-home scope root, rejects traversal/link/reparse/hard-link boundaries, and performs no enumeration |
| The envelope hashes different bytes from those parsed | the bounded Codex path captures once from one securely opened file and hashes/parses the same captured bytes |
| Source text or a local path leaks through the envelope | the envelope schema allows fixed metadata/counts only; source text, file name, and path are absent, while the enclosing evidence remains explicitly private |
| Repeated lifecycle snapshots inflate one completed item | coalesce only structured `item_completed` records by turn + item identity; preserve first position and use the latest valid snapshot |
| `task_complete` hides a late tool completion | retain the terminal and every later supported completed item in physical-record order; never interpret the terminal as an end-of-file assertion |
| Words such as “done”, “automation”, or “delegation” alter structure | completion and semantic exclusions require exact protocol discriminators; ordinary text never creates either state |
| A named Skill block leaks its name or local path | extract only official user text blocks into private evidence; the metadata envelope stores neither Skill blocks nor raw rollout identifiers |
| Crafted IDs alias two lifecycle identities | reject control-bearing IDs and derive private IDs from canonical JSON tuples rather than delimiter concatenation |
| A future or malformed user-input block silently loses a requirement | allow only current official text/image/audio/Skill/mention discriminators with required fields; unknown shapes are unsupported and make evidence incomplete |
| Forged normalization counters pass schema validation | require retained, duplicate, dropped, ordinary, terminal, and semantic-exclusion counts to conserve exactly against recognized records |
| Tiny records turn the 64 MiB byte cap into excessive parser work | fail closed after 1,000,000 physical records as well as at the byte cap |

## Residual risks

Pattern detectors have false positives and false negatives. Windows cannot offer the same
parent-directory descriptor binding used on POSIX, so it relies on reparse checks and repeated
identity validation. Repository-local Git configuration can still affect read-only answers;
redirecting inherited/global/system configuration is disabled. Parser formats may drift. A
person may still share the private bundle by mistake.
These are documented limits, not silently converted into guarantees.

The v0.2 host contract cannot prove that every Codex environment exposes equivalent thread APIs,
session formats, or privacy controls. Until a host adapter is implemented and tested, the three
mode workflows remain `implemented-unverified` and must disclose any missing source.
On Windows, the scoped input boundary relies on reparse checks and repeated identity validation
where POSIX `dir_fd` traversal is unavailable; the project does not claim identical kernel-level
guarantees across platforms.
On macOS, the root-owned `/var`, `/tmp`, and `/etc` compatibility aliases are narrowly mapped to
their fixed `/private` targets. The selected source is captured once, so its digest and parsing
cannot diverge; same-inode/same-size writes that restore mtime can evade the concurrent path
metadata check, so atomic source stability remains unknown. “No network client” also does not
prove that the user-selected filesystem is not remotely mounted.
The enclosing v0.1 `network_used: false` field is retained for schema compatibility and only means
that the core pipeline did not initiate network or remote-API code. Deterministic target/task
SHA-256 values are integrity bindings rather than anonymisation: a low-entropy reference can be
dictionary-checked and linked across private bundles. The bundle therefore remains private.
