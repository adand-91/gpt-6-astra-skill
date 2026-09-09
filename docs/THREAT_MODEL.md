# Threat model

## Protected assets and trust boundary

Protected assets include private conversations, client data, local paths, credentials, source code,
Git state, the truth of evidence, and the user's machine and external accounts. Every selected file,
report, Markdown fragment, filename, error message, repository configuration, and model suggestion
is untrusted data. None can become an instruction, approval, or scope expansion.

v1 accepts only an explicit target/window and explicit files below an approved scope root. It does
not discover history, projects, files, or external sources by default.

## Main threats and controls

| Threat | v1 control |
|---|---|
| A named target causes a scan of unrelated sessions or projects | One explicit target or derived time window, plus explicit files; no enumeration or automatic discovery. |
| A scope root points at the account home or filesystem root | Reject the actual account home directory and filesystem roots; do not trust an environment-variable alias as the only home check. |
| Link, traversal, hard-link, reparse, or replacement escapes the scope | Reject traversal, links/reparse points, non-regular files, and multiple hard links; bind component identities and descriptor identity. |
| A file changes during parsing or across a multi-source binding | Hold each descriptor through the operation; compare device/inode/size/mtime/ctime before and after. Source and report descriptors share the binding/handoff read domain. |
| Private text or path leaks into durable state or a report | Source packs store only opaque source identity, digest, and byte count; candidate/binding state is strict UTF-8 bounded metadata; share output remains separately gated. |
| Crafted state weakens a transition or integrity head | Exact schemas reject unknown fields, malformed booleans/counts, control characters, invalid IDs, duplicate physical aliases, stale expected heads, and invalid transitions. |
| Hidden Markdown makes a report look valid | Validate required content in human-visible Markdown; do not count frontmatter, HTML comments, or fenced blocks. Reject unknown report-frontmatter fields. |
| A final report or handoff implies authority to act | Binding requires a mechanically final report; handoff is identity/readiness-only. Neither command can edit, commit, publish, send, schedule, or approve. |
| Plugin installation broadens capability or installs code | The plugin is skills-only, checks the installed CLI, and has no MCP, hooks, downloader, updater, credentials, telemetry, or network runtime. |
| Output replaces existing work or follows a hostile parent | Create-only output, restrictive modes, checked parents, and descriptor-relative creation on supported POSIX hosts. |
| Large or non-UTF-8 JSON becomes an unbounded parser workload | State and report inputs have explicit UTF-8, byte, count, and object-shape limits; malformed data fails closed. |

## Platform-specific boundary

POSIX uses descriptor-relative traversal and output creation with `dir_fd` and `O_NOFOLLOW`; a
non-Windows platform without `dir_fd` fails closed instead of using an insecure fallback.

Windows output creation binds the checked parent to a non-share-delete directory `HANDLE` and uses
`NtCreateFile` with `RootDirectory` for one validated leaf. A protected DACL and delete-pending
transaction prevent caller bytes from becoming a committed path until write, flush, and a second
same-domain parent identity check pass; rollback uses only the exact child handle. Contract and
static regressions pass locally, but Windows-native API/fault-injection cases cannot run on macOS
and remain an explicit public-CI gate rather than a claimed local result.

## Residual risks

The checks detect ordinary concurrent drift but cannot promise one atomic point-in-time snapshot of
many files or defeat a hostile filesystem/kernel. Digest identities are not anonymisation and can
be linked for low-entropy inputs. Parser formats can drift; reports still require human judgment;
and a user can manually disclose a private artifact. Network-free core behavior does not prove the
selected filesystem is not remotely mounted.

Local `1.0.0` candidate evidence does not prove public cross-platform CI, a public tag or Release,
publisher identity, marketplace acceptance, external adoption, or eligibility for any programme.
