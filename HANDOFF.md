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

## 卡在哪儿

- No local product blocker is known. Public CI has not yet validated the exact commit that will be
  tagged, so tag and GitHub Release creation remain blocked until that run is green.
- Public release assets must be rebuilt from the final tagged source if publication-only docs
  change after the first CI gate, because README files are included in the distribution.
- Windows-native coverage is expected from public CI; it is not inferred from the local macOS run.
- No external-user adoption, repeat-use, or OpenAI programme eligibility is claimed.

## 下一步计划

1. Restamp bilingual files and rerun all 122 tests, diff checks, and Handoff freshness.
2. Commit and push only this Alpha 2 boundary to `main`; wait for its public cross-platform CI.
3. If green, make only factual publication-state updates, rebuild wheel/sdist and a basename-only
   `SHA256SUMS`, rerun the gates, push, and wait for the final exact-commit CI.
4. Create annotated tag `v0.2.0-alpha.2`, publish it as a non-latest GitHub prerelease, then
   re-download and verify all assets plus clean wheel/sdist installation.
5. Stop after Alpha 2 and report the release URL, evidence, and fresh GitHub Stars/Forks/Watchers.

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

- Status: Alpha 2 source restored and locally reverified; commit, push, public CI, tag, Release,
  public-download verification, and final status report remain.
- Version boundary: package `0.2.0a2`; intended annotated tag `v0.2.0-alpha.2`; no later version is
  included or authorised.
- Local gate: 122 tests on Python 3.12, translation sync, and diff check passed before this Handoff
  refresh; all gates will be rerun before push.
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
- Pre-publication local result: 122 tests passed on Python 3.12.13; translations and whitespace
  checks passed. Public CI and release-download evidence must be appended after they exist.

## 授权与禁止动作

- Authorised: commit/push the exact Alpha 2 boundary, wait for CI, create the annotated Alpha 2
  tag and non-latest prerelease, upload its three public assets, and verify public downloads.
- Not authorised: publish later queued versions, move existing tags, create Issues/PRs, promote,
  rename the repository, submit a plugin, apply to an OpenAI programme, send external messages, or
  reset/clean/stash the maintainer's cumulative worktree.
- Any source mismatch, failing local/public gate, tag/release conflict, or suspected private data
  stops publication and requires diagnosis within this same Alpha 2 boundary.

## 回滚

- Before tagging, correct an error with a reviewed forward commit; never rewrite shared history.
- After tagging, do not move or silently replace the tag or assets. Preserve evidence and use a
  separately authorised corrective release if required.
- The untouched cumulative development worktree and sealed final-candidate directory remain the
  recovery sources; neither may be destructively cleaned.
