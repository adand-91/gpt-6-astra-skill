# HANDOFF

## 我们在做什么

- Publish `v0.2.0-alpha.2` as the first of the remaining queued prereleases, without including any
  later local Beta, RC, plugin, or v1 work.
- Alpha 2's product boundary is one explicit, bounded, privacy-preserving Codex input envelope for
  a user-selected task export. It is not automatic Codex history retrieval or account access.
- The release source is an isolated worktree restored from the sealed Alpha 2 final-candidate
  snapshot. The maintainer's cumulative dirty worktree is not release input.

## 完成了什么

- Restored the sealed Alpha 2 source snapshot over `origin/main` in the isolated
  `codex/release-v0.2.0-alpha.2` worktree.
- Set the package version to `0.2.0a2` and added `codex-scan` plus
  `src/requirement_ledger/codex_input.py`.
- The scanner requires an explicit target and half-open time window, records source identity and
  record accounting, detects malformed/out-of-window data, and reports partial or unknown coverage
  rather than claiming completeness.
- Output uses digests instead of retaining raw target strings or source paths. Existing size,
  no-overwrite, safe-write, and validation boundaries remain active.
- Added `tests/test_codex_input_envelope.py` and updated the broader CLI, pipeline, transcript,
  safe-I/O, documentation, threat-model, architecture, checklist, and bilingual contract surfaces.
- Reverified the restored source on Python 3.12: 122 tests passed; translation sync and
  `git diff --check` passed before the release-record refresh.
- Verified sealed assets against the frozen record:
  - wheel SHA-256: `0190c7902e64ab8e8c98363421274d92343b974edf7bf53462ae2077d1d246cd`
  - sdist SHA-256: `ad888a21b17408d02a8a17120bc84cb9f9b0e2c53c7b57b4e906d31b4b95de6e`
- Published annotated tag object `00fb12747e93f9c48f24c434b5d329fbdad57bf4` at commit
  `fb49947627516bca463094becde16a63d047e2d6` as the non-latest
  [GitHub prerelease](https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.2).
- Re-downloaded all three public assets. Their hashes matched, both archives clean-installed as
  `0.2.0a2`, and Demo, audit init/check, `codex-scan`, private permissions, envelope assertions,
  and no-overwrite behaviour passed.

## 卡在哪儿

- No Alpha 2 publication blocker remains. The post-release factual record is the only repository
  housekeeping still pending.
- No external-user adoption, repeat-use, or OpenAI programme eligibility is claimed.

## 下一步计划

1. Restamp bilingual files, run diff and Handoff checks, and commit/push this factual post-release
   record to `main` without moving the immutable Alpha 2 tag.
2. Verify that record's CI, then stop and report the Release URL, evidence, and fresh GitHub
   Stars/Forks/Watchers.
3. Treat Alpha 3 as a future mapped candidate only; do not implement or publish it without a new
   user instruction.

## 踩过哪些坑

- The active development worktree contains later queued versions. Tagging or committing it would
  mislabel later code as Alpha 2; only the sealed snapshot in this isolated worktree is valid.
- Test execution can create untracked `__pycache__` directories. They are generated files and must
  be removed only from this isolated worktree, never via a broad cleanup of the maintainer tree.
- A candidate archive can prove the product boundary but not public provenance. The published
  artifacts must correspond to the final tagged commit and be independently re-downloaded.
- A green local macOS suite does not replace Linux/macOS/Windows CI. A failed public gate stops the
  release instead of weakening tests or moving the tag.
- Internal checksum records may contain absolute paths. Only a newly generated basename-only
  `SHA256SUMS` may be attached publicly.

## 当前任务汇总

- Status: `v0.2.0-alpha.2` is published and independently re-downloaded/verified; only this factual
  post-release record and its CI remain.
- Version boundary: package `0.2.0a2`; intended annotated tag `v0.2.0-alpha.2`; no later version is
  included or authorised.
- Verified gate: 122 local tests plus full public Python 3.10–3.13 Linux/macOS/Windows CI and
  built-artefact/security smoke passed on the tagged commit.
- GitHub snapshot before publication: 47 Stars, 1 Fork, 0 Watchers; stable `v0.1.1` remains latest.
- One-line result: Alpha 2 turns an explicit Codex export into a bounded evidence envelope without
  pretending to retrieve complete history or retaining user-selected target/path text.

## 当前架构与入口

- CLI and routing: `src/requirement_ledger/cli.py`.
- Codex input boundary: `src/requirement_ledger/codex_input.py`.
- Review/report pipeline: `src/requirement_ledger/pipeline.py`, `review.py`, and `transcript.py`.
- Safe output/error contracts: `src/requirement_ledger/safeio.py` and `errors.py`.
- Regression suite: `tests/test_codex_input_envelope.py` plus the existing `tests/` suite.
- User/release communication: `README.md`, `CHANGELOG.md`,
  `docs/release-notes/v0.2.0-alpha.2.md`, and their Chinese mirrors.

## 运行与依赖

- Supported Python: 3.10–3.13. Windows conditionally uses `tzdata>=2024.1`; Unix-like systems use
  the standard library for timezone data.
- Source test command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`.
- Translation gate: `python3 scripts/check_translation_sync.py`.
- Build: `python3 -m build --sdist --wheel`; build tooling is not a runtime dependency.
- Release smoke must clean-install both archives and exercise version, Demo, review, and
  `codex-scan` paths.

## 验证证据

- The private release archive retains the sealed Alpha 2 source snapshot; its local path is not
  published in this repository.
- Frozen wheel: `requirement_ledger-0.2.0a2-py3-none-any.whl`, SHA-256
  `0190c7902e64ab8e8c98363421274d92343b974edf7bf53462ae2077d1d246cd`.
- Frozen sdist: `requirement_ledger-0.2.0-alpha.2.tar.gz`, SHA-256
  `ad888a21b17408d02a8a17120bc84cb9f9b0e2c53c7b57b4e906d31b4b95de6e`.
- Tagged commit `fb49947627516bca463094becde16a63d047e2d6` passed public CI runs
  `33468720368` and `33468928114`: Python 3.10–3.13 on Linux, macOS, and Windows plus
  built-artefact/security smoke.
- Public wheel SHA-256:
  `6dbb7b104a4a094138b87a0931d60030f58b3f8cfd6188f575fad9cae9c9094c`; public sdist:
  `d50b607a18e910d4c4be1d0d9658fd58ad33330da9b7191cc063efc30e188d62`; public checksum file:
  `b19d5981b643bbcc5c929b28a852aa73a26eaad09098f83c55d29809907275f0`.
- Public downloads matched the approved files byte-for-byte and passed clean install plus the
  Alpha 2 command and privacy smokes.

## 授权与禁止动作

- Authorised batch completed: Alpha 2 exact boundary, CI, annotated tag, non-latest prerelease,
  three public assets, independent download verification, and this factual repository record.
- Not authorised: publish later queued versions, move existing tags, create Issues/PRs, promote,
  rename the repository, submit a plugin, apply to an OpenAI programme, send external messages, or
  reset/clean/stash the maintainer's cumulative worktree.
- Do not move the published Alpha 2 tag or replace its public assets.

## 回滚

- Before tagging, correct an error with a reviewed forward commit; never rewrite shared history.
- After tagging, do not move or silently replace the tag or assets. Preserve evidence and use a
  separately authorised corrective release if required.
- The untouched cumulative development worktree and sealed final-candidate directory remain the
  recovery sources; neither may be destructively cleaned.
