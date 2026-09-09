# Architecture

## v1.0.0 local-stable candidate

Requirement Ledger has one product core and one deliberately thin Codex distribution layer:

```text
one Codex host-selected task/project
                         |
                         v
       skills-only plugin quick audit guidance
       (plain-language, host-selected / unbound;
        no CLI report/source/candidate/binding claim)

explicit target + bounded time window + explicit files
                         |
                         v
             independent Python library and CLI
     (schemas, scoped I/O, review checks, private state)
                         |
                         +-- audit / daily / weekly review reports
                         +-- source pack + candidate ledger
                         +-- exact review binding + handoff check
                         |
                         v
       repository-local, skills-only Codex plugin
       (guidance and installed-CLI preflight; no second runtime)
```

The Python CLI is the authority for schemas, validation, privacy boundaries, and deterministic
verification. The repository-local marketplace plugin contains `plugin.json` and one focused
`SKILL.md`; it guides Codex to use an already installed compatible CLI. It has no MCP server,
app, hook, downloader, installer, model call, database, telemetry, credential, or network client.

The host-selected quick audit is intentionally not a shadow runtime. It is a plugin-guided Codex
summary over one host-selected boundary and must report itself as unbound. Reproducibility begins
only when the explicit-file CLI path creates and verifies the corresponding private artefacts.

The normative product boundary is [V1_STABLE_CONTRACT.md](V1_STABLE_CONTRACT.md). The plugin is
not an alternative implementation and cannot make a missing CLI compatible or authorize an action.

## Review and continuity flow

```text
explicit target/window
  -> explicit regular files below an approved scope root
  -> private source-pack/v1 (digest, byte count, opaque source identity)
  -> audit | daily | weekly final report
  -> candidate-current/v1 and candidate-ledger/v1 continuity
  -> review-binding/v1 (exact report bytes + current source/candidate heads)
  -> read-only handoff verification
  -> separately authorized, host-owned implementation
  -> same-oracle outcome verification
```

`audit` is one explicit target; `daily` and `weekly` derive an explicit half-open window from an
IANA timezone, reference time, and boundary hour. They are analysis-only: input selection never
grants implementation, a commit, a push, publication, scheduling, or an external message.

Candidate continuity is exact, opaque-ID state rather than semantic matching. Unresolved items
that are absent from a later review are carried forward; stale expected heads, invalid transitions,
and silent drops fail closed. Source packs contain only explicit scoped source descriptors, not
paths or source text. A final binding contains the exact UTF-8 report bytes, target digest, report
metadata, source-pack head, and candidate-state head. `review-handoff-check` verifies identity and
readiness only; it never grants execution authority.

## Integrity and privacy boundary

- Scope roots may not be a filesystem root or the actual account home directory. Inputs are
  explicit, regular, single-link files below the root; the CLI does not enumerate history,
  projects, or directories.
- Scoped reads bind device/inode, byte size, mtime, and ctime. The timestamps are part of the
  in-memory integrity snapshot checked before and after the descriptor-held read.
- Source descriptors and the report descriptor are opened in one held read domain for binding or
  handoff verification, then rechecked before the result is returned. This detects replacement or
  ordinary in-place drift during the operation; it is not a filesystem-wide atomic snapshot.
- JSON state is strict UTF-8, byte/count bounded, object-only, and rejects unknown fields,
  malformed controls, duplicate aliases, and control-bearing identifiers. Private state persists
  hashes and bounded metadata, not raw source content or local paths.
- Review parsing validates visible Markdown rather than trusting text hidden in frontmatter,
  comments, or fenced blocks. Unknown frontmatter fields and invisible-only required sections are
  rejected.
- Private outputs are create-only and restrictive where supported. No command modifies the chosen
  source, repository, remote, or account.

## Platform boundary

On POSIX, output creation and scoped input traversal use descriptor-relative paths with
`O_NOFOLLOW`. A non-Windows platform that lacks `dir_fd` support stops rather than falling back to
an unsafe relative create path.

Windows output creation now binds the preflight parent identity to a non-share-delete directory
`HANDLE`, creates one validated leaf with `NtCreateFile(RootDirectory=...)`, applies a protected
DACL, and keeps the new object delete-pending until write, flush, and same-domain parent identity
checks pass. Failures roll back by the exact child handle; the implementation never deletes by
path. The cross-platform contract tests pass locally, while the Windows-native API and fault-
injection cases are intentionally recorded as unexecuted on macOS and remain a public-CI gate.

## Exclusions and residual risk

v1 does not provide automatic task/history discovery, background monitoring, network or trend
collection, model scoring, semantic merge, automatic edits, commit/push/release, GUI, hosted
service, database, OAuth, MCP, Apps SDK widgets, or IDE-extension guarantees.

Digest bindings prove byte identity, not truth, authorship, quality, or authorization; low-entropy
references can be dictionary-linked, so every pack remains private. Filesystem metadata cannot
prove a globally atomic multi-file instant, remote mounts may have different semantics, and parser
compatibility depends on maintained fixtures. A local stable candidate is not a Git tag, GitHub
Release, public CI result, or accepted public-plugin submission.
