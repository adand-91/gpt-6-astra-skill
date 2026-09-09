# Release checklist

This is the v1 release record. Historical v0.1 public-release facts remain in the repository
history; they are not evidence for the local v1 candidate.

## v1.0.0 local-stable gate

Mark a box only with current command output or a reviewed artifact in the local release-evidence
directory. The local gate below passed on 2026-08-30. Local stable is intentionally narrower than
public publication.

### 2026-08-31 reopened Codex qualification

- [x] README, stable contract, plugin manifest, Skill, CLI reference, and regression cases describe
  the same two levels: `host-selected / unbound` quick audit versus evidence-bound CLI review.
- [x] v1 CLI audit remains explicit-window evidence workflow; no schema/runtime change was hidden
  behind the new quick-audit wording.
- [x] Refresh the installed local plugin snapshot, start a fresh Codex task, and pass the selected
  project quick-audit case without requesting a window, JSONL, scope root, or file path.
- [x] Rerun the full source/distribution/translation/build/archive qualification and freeze new
  candidate hashes after the final documentation and plugin bytes settle.

### Contract and scope

- [x] `V1_STABLE_CONTRACT.md`, architecture, threat model, gap ledger, changelog, and plugin docs
  describe the same core/plugin boundary and exclusions.
- [x] No live private transcript, real credential/token/session ID, maintainer-specific absolute
  path, or unintended build/cache output is present in the wheel, sdist, or source snapshot.
  Reviewed synthetic privacy canaries in tests and standard setuptools packaging metadata are
  explicit exceptions; neither is represented as live private evidence.
- [x] No feature was added after the RC freeze; any correction rebuilt and revalidated the RC.

### Core verification

- [x] Full unit suite, focused privacy/security regressions, `compileall`, translation check, and
  `git diff --check` pass.
- [x] Built wheel and sdist install in clean environments and report the exact `1.0.0` version.
- [x] Archive inspection confirms the Python distribution excludes cache/bytecode/private evidence
  and the Codex plugin remains a separate repository distribution layer.
- [x] Three maintainer-owned explicit workflows (`audit`, `daily`, `weekly`) pass, including
  positive and negative source/candidate/binding/handoff cases.
- [x] Source packs, candidate ledgers, report bindings, and handoff checks reject drift, stale
  heads, unknown fields, invisible-only Markdown, non-UTF-8/oversized state, and overwrite paths.
- [x] Plugin manifest/skill validators and a real local marketplace add/install/remove cycle pass;
  the compatible-CLI preflight stops without installing software when unavailable.

### Platform gate

- [x] Supported local Python/OS evidence is recorded with exact versions and command results.
- [x] POSIX descriptor-relative creation/traversal and non-Windows missing-`dir_fd` fail-closed
  regressions pass.
- [x] Windows parent `HANDLE` + `NtCreateFile(RootDirectory=...)` output creation, one-byte delete
  disposition ABI, protected DACL, same-domain parent binding, and handle-only rollback are present
  and pass local contract review. Windows-native tests are recorded as skipped on macOS and remain
  a public-CI gate; they are not claimed as locally executed.

### Evidence and handoff

- [x] Final wheel, sdist, source snapshot, test count, smoke outputs, and SHA-256 values are saved
  outside the source tree in the dated local release-evidence directory.
- [x] `HANDOFF.md` is newer than the final program/configuration change and passes its validator.
- [x] Local context/checkpoint identifies the exact candidate, remaining public actions, and no
  broader authority than the local train.

## Public actions — intentionally not performed by the local gate

- [ ] Commit the v1 release candidate.
- [ ] Push a v1 branch or release commit.
- [ ] Run and verify public CI for the pushed v1 commit.
- [ ] Create an annotated `v1.0.0` tag.
- [ ] Publish a GitHub Release or upload public assets.
- [ ] Re-download and verify public artifacts.
- [ ] Submit the Codex plugin to any public directory or marketplace.
- [ ] Promote the project, apply to an external programme, or send an external message.

Each unchecked action needs a separate current authorization and its own evidence. None is implied
by a passing local-stable gate.
