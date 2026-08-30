# HANDOFF

## 我们在做什么

- Goal: publish and verify `v0.2.0-alpha.1`, then record a ten-release-day path to stable
  `v0.2.0`.
- Release result: annotated tag `v0.2.0-alpha.1`, PEP 440 package `0.2.0a1`, a non-latest
  GitHub prerelease, and three publicly re-downloaded/verified assets.
- Current batch: land factual publication evidence and the maintainer-requested daily candidate
  sequence without moving the released tag or mixing in later local Beta, RC, or v0.3 drafts.
- Not in scope: no Issue, PR, promotion post, programme application, automatic schedule,
  telemetry, unattended target edit, unrelated-history read, or empty/backdated release.

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
- Added bilingual `UPDATE_MAP` and revised `ROADMAP`. The final release train targets one
  substantive candidate per successful release day:
  `alpha.1 → alpha.2 → alpha.3 → beta.1 → beta.2 → beta.3 → rc.1 → rc.2 → rc.3 → v0.2.0`.
- Extended CI release smoke to install the built wheel, create/check a named audit, verify private
  permissions and no-overwrite failure, and require the update map and review test in the sdist.
- The first public CI run passed Linux and macOS but proved that Windows Python has no system IANA
  timezone database. The corrected package declares `tzdata>=2024.1` only on Windows, the matrix
  installs platform dependencies, and a regression makes a no-dependency Windows error actionable.
- Added an Alpha-specific release-checklist section. Internal archived evidence and path-bearing
  checksums are explicitly excluded from public assets.
- Corrected commit `243b01ac5be88825ec4a1f4f9c5cec3b2841a90e` passed public CI run
  `33291029715`: Python 3.10–3.13 on Linux, macOS, and Windows plus built-artefact/security smoke.
- Created annotated tag object `856f4d0fd198a74825f134289af3b0475042ec85` and the public
  non-latest [prerelease](https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.1).
- Re-downloaded `requirement_ledger-0.2.0a1-py3-none-any.whl`,
  `requirement_ledger-0.2.0a1.tar.gz`, and `SHA256SUMS`; all matched the approved local files.
  Both archives clean-installed and passed version, Demo, audit initialisation, and report checks.

## 卡在哪儿

- Current blocker: no Alpha publication blocker remains. This factual evidence/map commit must
  still reach `main` and pass its own CI before the isolated release worktree is considered closed.
- Product gap after Alpha 1: the installed package does not retrieve Codex history and cannot
  initialise daily/weekly reviews. Those features remain visible targets, not shipped claims.
- Adoption gap: no external-user installation or repeat-use evidence is claimed.

## 下一步计划

1. Run translation sync, all 113 tests, diff checks, and Handoff freshness on this documentation
   record; commit/push it to `main` without moving the Alpha tag and verify public CI.
2. Build Alpha 2 in a new exact candidate boundary: one explicit bounded Codex input envelope with
   identity/digest, target/window, included/excluded coverage, and fail-closed path/size/drift rules.
3. Continue only through the daily sequence in `UPDATE_MAP.md`; a failed candidate gate shifts
   every dependent target rather than producing an empty Release.

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
- A day in the update map is the next successful release day, not unconditional calendar
  permission. Empty versions, backdating, failed-gate bypass, and fabricated maintenance are
  excluded.
- Standard-library `zoneinfo` is not self-contained on Windows. Calling the package “zero runtime
  dependency everywhere” hid a real portability requirement; docs now distinguish Unix-like
  systems from Windows and CI installs the conditional database.

## 当前任务汇总

- Status: `v0.2.0-alpha.1` is published and independently re-downloaded/verified; only its
  post-release evidence/map commit and CI remain as repository housekeeping.
- Current version: package `0.2.0a1`, published annotated tag `v0.2.0-alpha.1`; `v0.1.1`
  remains the latest stable Release.
- Verified source result: 113 tests, full cross-platform CI, clean wheel/sdist installs,
  deterministic Demo, private/no-overwrite audit scaffold, and strict report check.
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
- Corrected tagged commit `243b01ac5be88825ec4a1f4f9c5cec3b2841a90e`: CI run
  `33291029715` passed all 12 Python/OS matrix jobs and built-artefact/security smoke.
- Public wheel SHA-256:
  `3123b30db1610e0b930c0d0f26a3a24ec3dbe47917d5da7d1f7c3b800dac615b`.
- Public sdist SHA-256:
  `1e5407f5f48d8bdd19f18749aa6bc978002415a90061426cf5bef9b40103ae05`.
- Public `SHA256SUMS` SHA-256:
  `c7f4789bc5d26fc686f49194f3da48d3426fd75c8326a1163b73edd627406011`.
- The public downloads matched local approved assets byte-for-byte; checksum verification, dual
  clean installation, version, deterministic Demo, `review-init`, and `review-check` passed.

## 授权与禁止动作

- Authorised in this batch: add/push this factual post-release evidence and daily update map.
  The maintainer requested the ten-release-day direction; each exact candidate still requires its
  own coherent increment, passing gate, accurate notes, and exact-commit publication decision.
- Not authorised: Issues, PRs, promotion posts, programme applications, schedules, notifications,
  unrelated/full history reads, deletion of evidence, or destructive changes to the maintainer
  worktree.
- A failed local or public gate stops tag/release creation; it does not authorise weakening the
  test, rewriting evidence, or publishing a partially checked asset.

## 回滚

- Revert an incorrect evidence/map change with a new reviewed commit; do not rewrite history.
- The published Alpha tag and assets are immutable for this batch. If release evidence becomes
  invalid, preserve the record and publish a corrective prerelease or factual withdrawal under a
  separate maintainer decision; never move the tag silently.
- The original dirty maintainer worktree remains the recovery source for post-Alpha drafts and must
  not be reset, cleaned, stashed, or wholesale overwritten.
