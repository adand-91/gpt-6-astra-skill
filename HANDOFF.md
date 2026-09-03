# HANDOFF

## 我们在做什么

- Publish `v0.2.0-alpha.3` as the next non-latest prerelease in the existing release train.
- Its only product increment is bounded normalization of supported modern Codex rollout records.
- Reconstruct the release from `origin/main` in an isolated worktree so the public Alpha 2 record
  is preserved and the maintainer's later cumulative work remains untouched.

## 完成了什么

- Verified the unique frozen Alpha 3 source, wheel, sdist, and checksums.
- Reused only the audited Alpha 2-to-Alpha 3 implementation, tests, CI, contracts, and release-note
  delta; excluded generated egg-info and every Beta/RC/v1/Jarvis change.
- Added `codex-modern-normalization/v1`, `codex-input-envelope/v2`, ordered item/terminal accounting,
  structured exclusions, canonical tuple hashing, strict input/status validation, exact record
  conservation, and the 1,000,000-record work cap.
- Preserved Alpha 2's public tag, CI, asset hashes, and re-download evidence in the reconstructed
  documentation.
- Repeated 132 source tests, 19 focused tests, translation sync, compile, and diff checks. Fresh
  wheel and sdist builds both report `0.2.0a3`; clean installs, deterministic Demo, audit,
  no-overwrite, private permissions, modern envelope privacy, and extracted-sdist tests passed.
- Initial release commit `5d97742` passed public CI run `33707942357`: all 12 Python 3.10–3.13
  Linux/macOS/Windows jobs plus the built-artefact and fail-closed security smoke succeeded.
- Published annotated tag object `af32da5b81c12317177042875ffd08a8f03b816c` at commit
  `dfa04a0d21ff0aca5c97d87b40546c58fe39d199` as the non-latest
  [GitHub prerelease](https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.3).
- Re-downloaded all three public assets; hashes matched, wheel and sdist clean-installed as
  `0.2.0a3`, and the downloaded wheel passed deterministic Demo, audit, modern envelope privacy,
  and item/terminal assertions.

## 卡在哪儿

- No known source-design blocker remains.
- No Alpha 3 publication blocker remains. Only this factual post-release record and its CI remain.
- External-user adoption and OpenAI programme eligibility remain unproven and are not release
  claims.

## 下一步计划

1. Commit and push this factual post-release record to `main` without moving the immutable tag.
2. Verify the record's CI, report release metrics, and stop.
3. Keep larger Jarvis/usability changes for `v1.0.0-rc.1`; earlier candidates follow the normal
   release cadence and still require separate authorization.

## 踩过哪些坑

- The frozen Alpha 3 source predates the public Alpha 2 release and incorrectly calls Alpha 2
  unpublished. Only its audited delta is valid; the snapshot must not overwrite `origin/main`.
- Frozen candidate archives cannot be uploaded as final public assets because corrected public
  documentation changes the sdist. Public files must be rebuilt from the exact tagged commit.
- The active development worktree contains later queued versions. It must never be tagged,
  cleaned, reset, or used as Alpha 3 release input.

## 当前任务汇总

- Status: `v0.2.0-alpha.3` is published and independently re-downloaded/verified; only this factual
  post-release record and its CI remain.
- Version boundary: package `0.2.0a3`; intended tag `v0.2.0-alpha.3`.
- Local release evidence: 132 source tests, 19 focused tests, builds, dual clean installs,
  deterministic Demo, audit, privacy, and fail-closed checks passed.
- Public release evidence: final CI runs `33708129443` and `33708228485` passed; public asset
  hashes are recorded below and were independently verified.
- Authorised: exact Alpha 3 commit/push/tag/prerelease/assets/re-download verification and factual
  release record. Not authorised: later versions, promotion, rename, plugin/programme submission,
  Issues, PRs, or unrelated external messages.

## 当前架构与入口

- CLI/routing: `src/requirement_ledger/cli.py` and `src/requirement_ledger/pipeline.py`.
- Input boundary: `src/requirement_ledger/codex_input.py`.
- Modern rollout adapter: `src/requirement_ledger/transcript.py`.
- Regression suite: `tests/test_codex_modern_normalization.py` and
  `tests/test_codex_input_envelope.py` plus the existing `tests/` suite.

## 运行与依赖

- Supported Python: 3.10–3.13. Windows conditionally uses `tzdata>=2024.1`.
- Source tests: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`.
- Translation gate: `python3 scripts/check_translation_sync.py`.
- Build: `python3 -m build --sdist --wheel`; build tooling is not a runtime dependency.

## 验证证据

- Frozen wheel SHA-256: `a46fa9b62dd5c8e702419743e312820214c5527f1da7d7405f26b3769e224b99`.
- Frozen sdist SHA-256: `5c813a5fc3cf6f93f187b2cf02fe345e0f4be381567c8d2618faa57060601687`.
- The frozen wheel's Python modules and the frozen sdist's shared files match the source snapshot
  byte-for-byte. The public hashes below were generated from the tagged commit.
- Public wheel SHA-256: `c809a6bd92810a8509401e0d7c93eb976d073db5aafa8d97244c941a929ea7ec`.
- Public sdist SHA-256: `1a7deb8725ada52470f0b9739b93aaea47659eedf75b2bf475774b3576d2a740`.
- Public checksum-file SHA-256: `18083577d5bb9fcd4020be11a8cab0900904d23e9bb0e9db605b2894f54f8164`.

## 授权与禁止动作

- Authorised: publish the exact Alpha 3 boundary and verify it publicly.
- Not authorised: publish later versions, move old tags, replace old assets, promote, rename,
  submit a plugin/programme application, create Issues/PRs, or alter the dirty development tree.

## 回滚

- Before tagging, fix a failed gate with a reviewed forward commit or stop the release.
- After tagging, never move or silently replace the tag or assets; use a separately authorised
  corrective release if required.
