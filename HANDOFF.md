# HANDOFF

## 我们在做什么

- Goal: publish `v0.2.0-alpha.1`, the first installable Codex-first named-target audit preview,
  without including later local Beta, RC, or v0.3 work.
- Current batch: restore the sealed `0.2.0a1` source onto a clean `origin/main` worktree, improve
  bilingual release communication, add a gate-driven ten-day update map, and pass the complete
  release pipeline before a GitHub prerelease.
- Release shape: annotated tag `v0.2.0-alpha.1`, PEP 440 package version `0.2.0a1`, GitHub
  `prerelease=true`, and not the latest stable release.
- Not in scope: no Issue, PR, promotion post, programme application, schedule, telemetry,
  unattended target edit, unrelated-history read, or publication of any other version.

## 完成了什么

- Created an isolated release worktree from `origin/main`; the maintainer's mixed post-Alpha dirty
  worktree was not reset, cleaned, stashed, or used as release input.
- Restored the sealed Alpha source while retaining repository control files (`.github/**`,
  `.gitattributes`, `.gitignore`) and excluding sdist-generated `PKG-INFO`, `setup.cfg`, and
  `src/requirement_ledger.egg-info/**` files.
- Package version is consistently `0.2.0a1`. The v0.1.1 CLI and evidence schemas remain
  compatible.
- Added `review-init --mode audit`: one explicit target, half-open time window, IANA timezone,
  private file permissions where supported, zero retrieved sources, incomplete coverage,
  `analysis-only` authority, and no-overwrite output.
- Added `review-check` and a standalone delegating script. The single packaged validator checks
  schema, mode, status, target, window ordering, offset/timezone agreement, required sections,
  evidence labels, candidate state, ecosystem fields, source structure, and authorisation.
- Added bilingual host contracts and audit/daily/weekly reference templates. Alpha 1 initialises
  only audit; daily and weekly are documentation/validation surfaces, not installed init modes.
- Rewrote the bilingual Alpha release notes around “what changed / what problem it solves / quick
  start / verified gate / known limits”.
- Added bilingual `UPDATE_MAP` and revised `ROADMAP`: stable v0.2 is a ten-day target with Alpha 2,
  Beta 1, RC 1, RC 2, and stable release decisions governed by exit gates rather than dates alone.
- Extended CI release smoke to install the built wheel, create/check a named audit, verify private
  permissions and no-overwrite failure, and require the update map and review test in the sdist.
- The first public CI run passed Linux and macOS but proved that Windows Python has no system IANA
  timezone database. The corrected package declares `tzdata>=2024.1` only on Windows, the matrix
  installs platform dependencies, and a regression makes a no-dependency Windows error actionable.
- Added an Alpha-specific release-checklist section. Internal archived evidence and path-bearing
  checksums are explicitly excluded from public assets.

## 卡在哪儿

- Current blocker: initial CI run `33290681748` failed all four Windows jobs because `tzdata` was
  absent; Linux and macOS passed. The conditional dependency fix has not yet passed its new public
  CI run, so no tag or Release exists.
- Publication gates still open: final local build and clean-install checks, commit/push, public CI,
  annotated tag, GitHub prerelease, public asset re-download, checksum verification, and a
  post-release evidence commit.
- Product gap after Alpha 1: the installed package does not retrieve Codex history and cannot
  initialise daily/weekly reviews. Those features remain visible targets, not shipped claims.
- Adoption gap: no external-user installation or repeat-use evidence is claimed.

## 下一步计划

1. Run full source tests, translation sync, compile, Skill structure validation, diff/privacy
   review, and Handoff freshness checks on this worktree.
2. Build wheel and sdist from the final source; test the extracted sdist; clean-install both;
   verify version, deterministic demo, audit create/check, mode `0600`, and no-overwrite.
3. Generate a basename-only `SHA256SUMS`; confirm artefacts and source contain no private local
   path, task identifier, private evidence, bytecode, cache, or later-version module.
4. Commit the exact Alpha source and push it to `main`; do not tag while public CI is pending or
   failing.
5. After the exact commit is green, create annotated tag `v0.2.0-alpha.1`, push it, and create a
   non-latest GitHub prerelease with the verified wheel, sdist, and checksum file.
6. Re-download the public assets, recheck hashes and install/smoke, then add publication evidence
   to `main` without moving the release tag.

## 踩过哪些坑

- The archived Alpha checksum file contains private absolute paths. The archived wheel/sdist are
  integrity-valid, but the checksum file and internal evidence/logs must not be uploaded. Public
  artefacts are rebuilt and receive a basename-only checksum file.
- A source distribution is not a Git checkout. Restoring it blindly would delete CI/control files
  and add generated metadata. The release reconstruction overlays only real source files onto
  `origin/main`.
- The maintainer worktree already contains later Beta, RC, and v0.3 modules. Tagging its HEAD or
  committing its entire diff would mislabel later features as Alpha 1; the isolated worktree is the
  release source of truth.
- Alpha ships daily/weekly templates and validation vocabulary, but the CLI deliberately rejects
  `review-init --mode daily|weekly`. Release notes now state this explicitly.
- A day in the update map is a decision target, not a promise to publish. Empty versions,
  backdating, and fabricated maintenance are excluded.
- Standard-library `zoneinfo` is not self-contained on Windows. Calling the package “zero runtime
  dependency everywhere” hid a real portability requirement; docs now distinguish Unix-like
  systems from Windows and CI installs the conditional database.

## 当前任务汇总

- Status: the first public CI attempt failed on Windows; a bounded portability correction is
  implemented locally, and publication remains stopped until its full local and public gates pass.
- Current version: package `0.2.0a1`, planned annotated tag `v0.2.0-alpha.1`; public stable release
  remains `v0.1.1` until the prerelease is verified.
- Corrected source result: 113 tests after translation restamping; full rebuild and public CI must
  be repeated before publication.
- One-line result: Alpha 1 is an installable, privacy-first starting point and mechanical contract
  checker for one named audit, not yet an automatic context retriever or three-mode scheduler.

## 当前架构与入口

- CLI: `src/requirement_ledger/cli.py`; version: `src/requirement_ledger/__init__.py`.
- Alpha review contract and scaffold: `src/requirement_ledger/review.py`.
- Standalone checker: `scripts/check_review_report.py`; regression suite:
  `tests/test_review_report.py`.
- Host product contract: `V0.2_HOST_CONTRACT.md`; mode/context/personalisation references are in
  `references/`.
- Public communication: `README.md`, `CHANGELOG.md`, `docs/release-notes/`, `UPDATE_MAP.md`, and
  `ROADMAP.md`; Chinese mirrors are maintained alongside them.
- Release policy and evidence index: `docs/RELEASE_CHECKLIST.md`.

## 运行与依赖

- Supported runtime: Python 3.10–3.13. Unix-like systems use the standard library only; Windows
  conditionally installs `tzdata>=2024.1` because the OS has no IANA timezone database.
- Build backend: setuptools through PEP 517; build tooling is not a runtime dependency.
- Source test command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`.
- Translation gate: `python3 scripts/check_translation_sync.py`.
- Build command: `python3 -m build --sdist --wheel` in an isolated build environment.
- CLI smoke: `requirement-ledger review-init ...` followed by
  `requirement-ledger review-check REPORT`.

## 验证证据

- Independent release audit verified the sealed wheel, sdist, source snapshot, versions, and
  hashes, and identified the absolute-path checksum problem before publication.
- Archived candidate source and extracted sdist agree byte-for-byte for 100 packaged files; the
  wheel's eleven Python modules agree with the same source.
- Initial commit `a880e9b48c921f5c32c9e362f5848de420eb9f52`: CI run `33290681748`
  passed all Linux/macOS jobs and failed all Windows jobs at IANA timezone loading; release smoke
  was skipped. No tag or Release was created.
- Corrected source adds the conditional Windows dependency and one missing-database regression,
  bringing the suite to 113 tests. Translation sync and final rebuild gates must be rerun after
  this Handoff update.
- Final artefact hashes and public CI run are intentionally not embedded here because they are
  generated after this source is committed. They must be attached/recorded as post-build and
  post-release evidence.

## 授权与禁止动作

- Authorised: prepare and commit the exact Alpha source; push it to `main`; create and push the
  annotated Alpha tag after CI passes; upload the verified wheel, sdist, and checksum file; create
  and verify a GitHub prerelease; add a factual post-release evidence commit.
- Not authorised: Issues, PRs, promotion posts, programme applications, schedules, notifications,
  unrelated/full history reads, other versions, deletion of evidence, or destructive changes to
  the maintainer worktree.
- A failed local or public gate stops tag/release creation; it does not authorise weakening the
  test, rewriting evidence, or publishing a partially checked asset.

## 回滚

- Before push, remove only the isolated release worktree/branch after preserving evidence; the
  maintainer worktree and public repository remain unchanged.
- After push but before tagging, fix or revert through a new reviewed commit; do not rewrite
  history or force-push.
- After prerelease publication, `v0.1.1` remains the latest stable release. Do not move the tag or
  delete the prerelease without a separate maintainer decision; publish a corrective prerelease or
  factual withdrawal note if evidence requires it.
