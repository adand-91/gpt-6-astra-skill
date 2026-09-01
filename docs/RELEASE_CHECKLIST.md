# Release checklist

Use this for every public version. A checked box must point to command output or a reviewed file.

## Scope

- [x] Version and milestone are coherent; no filler commit or backdated activity.
- [x] Scope ledger marks every requirement done, partial, cancelled, or blocked.
- [x] Known gaps remain visible in `docs/PROJECT_GAPS.md`.

## Mechanical gates

- [x] `python3 -m unittest discover -s tests -v`
- [x] `python3 -m compileall -q src scripts tests`
- [x] `python3 scripts/check_translation_sync.py`
- [x] wheel and sdist build in an isolated temporary directory
- [x] clean wheel installation exposes `requirement-ledger --version`
- [x] synthetic demo is byte-deterministic across two runs
- [x] explicit-input real-project smoke test leaves the Git snapshot unchanged
- [x] privacy canary blocks before the requested report file exists

## Human gates

- [x] Final diff contains no private transcript, path, credential-bearing remote, token, session
  ID, or build output.
- [x] README installation and demo commands were run from a clean wheel installation.
- [x] CHANGELOG and release notes state capabilities and limitations accurately.
- [x] Security and compatibility implications were reviewed.
- [x] Tag, push, and GitHub Release each have current maintainer authority.

## Pre-release evidence — 2026-08-28

- Unit suite: 96 tests, exit 0.
- Translation checker: `TRANSLATIONS_IN_SYNC`, exit 0.
- Compile and seven targeted fail-closed security regressions: exit 0.
- Wheel and sdist were built from the release candidate; final post-commit hashes are recorded on
  the GitHub Release so this source file does not create a self-referential sdist hash.
- Clean wheel and sdist installs both reported `requirement-ledger 0.1.0`.
- Two installed demo outputs compared byte-for-byte with no difference.
- Explicit-input smoke produced private evidence and left `git status` unchanged.
- Public cross-platform CI remains a post-push gate before the tag and GitHub Release.
- First public CI run `33152409147` passed Linux/macOS and exposed Windows CRLF hash drift;
  `.gitattributes` now fixes repository text to LF and the release remains blocked until rerun.
- Second public CI run `33152855005` proved LF normalisation on three Windows Python versions,
  then exposed a Windows Python 3.12 path-stat/handle-stat mismatch. Transcript binding now checks
  same-file identity separately from stable size/mtime content metadata; a new regression covers it.
- Third public CI run `33153226392` proved the transcript fix on Windows Python 3.12, then exposed
  the same false-positive metadata comparison in test-log binding on Windows Python 3.13. The
  test-log reader now uses same-file identity plus stable size/mtime checks and keeps its single
  descriptor, regular-file, single-link, size-limit, and read-after drift guards. A synthetic
  cross-platform regression covers differing path/handle metadata.
- Fourth public CI run `33153795367` passed all 12 Python/OS matrix jobs, including Windows Python
  3.13, and built and installed both artefacts. Its final source-level security subset could not
  import the `src/` package because that isolated job lacked `PYTHONPATH`; the step now binds
  `PYTHONPATH=src`. This was a CI harness defect, not a product-test failure.
- Fifth public CI run `33154009605` passed all 12 Python 3.10–3.13 × Ubuntu/macOS/Windows jobs and
  the complete built-artefact/security smoke. This is the first fully green public release gate.

## After release — follow-up, not a pre-release gate

- [x] Verify the public tag, source archive, README, install path, and demo.
- [ ] Watch the first real user path for parser, privacy, packaging, and error-message findings.
- [ ] Open follow-up work only for real evidence; do not manufacture activity.

## v0.1.1 pre-release evidence — 2026-08-28

- Unit suite: 97 tests, exit 0; translation checker: `TRANSLATIONS_IN_SYNC`; compile and
  `git diff --check`: exit 0.
- The documented synthetic Skill case produced baseline exit `1`, after exit `0`, validation
  `improved`, conservative scope `unknown`, and no raw failure text in its report.
- Wheel and sdist both built as `0.1.1`, installed in separate clean virtual environments, and
  exposed `requirement-ledger 0.1.1`.
- Two installed Demo outputs were byte-identical.
- The sdist contains both roadmaps, both Skill-case documents, bilingual README and Skill files,
  and contains no bytecode, cache directory, or `.private.json` evidence.
- Final artefact hashes must be regenerated from the release commit. Public CI, tag, Release,
  public re-download, and publication evidence remain blocked until the release commit is pushed.
- Implementation commit `d4d079cdd680bae707c1a05fa16ecf6e4fe67267` passed public CI run
  `33158962532`: all 12 Python/OS matrix jobs and the built-artefact/security smoke succeeded.
  The final evidence-only commit must pass the same workflow before tagging.

## Public release evidence — 2026-08-28

- Final tagged commit: `ebda35154b0256395d46345e748e2be445241487`.
- Final CI run `33154303073`: all matrix and release-smoke jobs passed.
- Release: `https://github.com/adand-91/requirement-ledger/releases/tag/v0.1.0`.
- Downloaded wheel SHA-256: `34c9df440d9896c6413d663b266c764649d260975ad2856b31c6de753cbdf050`.
- Downloaded sdist SHA-256: `3c4836002c1b6660d75897b1e31ca068f87396d848ad28b75db65833a2a125fc`.
- The downloaded wheel installed with `--no-deps`, reported `requirement-ledger 0.1.0`, and
  completed the synthetic Demo.

## v0.1.1 public release evidence — 2026-08-28

- Final tagged commit: `d07c13f91b119acf55135a504b8ba993f6b1aaf9`; annotated tag object:
  `d845481c973ab90a7d804db5cb7ea210a78e9224`.
- Final pre-tag CI run `33159107505`: all 12 Python/OS matrix jobs and the built-artefact/security
  smoke passed.
- Release: `https://github.com/adand-91/requirement-ledger/releases/tag/v0.1.1`.
- Downloaded wheel SHA-256: `39ec5c44fe62818d5a8057609d68328e74bf7cb605044bac934f81b96f345477`.
- Downloaded sdist SHA-256: `defde8eceace64ef908176602a9257b14d0aed8ee46b379011b8e76f79bb9f15`.
- The downloaded wheel installed with `--no-deps`, reported `requirement-ledger 0.1.1`, and
  completed the five-file Demo with validation status `improved`.
- Post-release publication-evidence commit `4b8c514a5dc29e7bded1eef2fe310c62e6b52cf3` passed public
  CI run `33159477520`, leaving `main` green after the release record was added.

## v0.2.0-alpha.1 pre-release evidence — 2026-08-30

- The frozen `0.2.0a1` source snapshot and its source distribution agree byte-for-byte for all
  100 packaged files; the wheel's eleven Python modules agree with the same snapshot.
- A clean release worktree was created from `origin/main`. It preserves `.github/**`,
  `.gitattributes`, and `.gitignore`, and excludes sdist-generated `PKG-INFO`, `setup.cfg`, and
  `src/requirement_ledger.egg-info/**` files.
- The Alpha contains only the named-target audit scaffold, strict review checker, and supporting
  host contracts/templates. Later Codex-export, candidate-ledger, report-pack, report-binding,
  handoff-verification, and Skill-health implementations are excluded.
- The initial sealed source passed 112 tests. The bounded Windows timezone correction added one
  regression, bringing the final source and extracted-sdist suites to 113 tests; translation sync,
  compile, `git diff --check`, dual clean installs, deterministic Demo, audit permission, and
  no-overwrite smokes all passed.
- The archived candidate checksum file used private absolute paths and is internal evidence only.
  Public artefacts must be rebuilt from the release commit and accompanied by a newly generated
  basename-only `SHA256SUMS`.
- Maintainer authority covered the exact release commit, annotated tag
  `v0.2.0-alpha.1`, three assets, GitHub prerelease, public re-download verification, and this
  factual evidence record. It did not cover Issues, PRs, promotion, programme applications, or
  another version.
- Initial public CI run `33290681748` passed all Linux and macOS jobs but failed all four Windows
  jobs because Windows does not provide an IANA timezone database for standard-library `zoneinfo`.
  The run is retained as failure evidence; no tag or Release was created.
- The correction declares `tzdata>=2024.1` only on Windows, installs platform dependencies in the
  matrix, and adds an actionable missing-database regression. Corrected commit `243b01a` repeated
  every local artefact gate and passed public CI run `33291029715` before publication.

## v0.2.0-alpha.1 public prerelease evidence — 2026-08-30

- Tagged commit: `243b01ac5be88825ec4a1f4f9c5cec3b2841a90e`; annotated tag object:
  `856f4d0fd198a74825f134289af3b0475042ec85`.
- Final pre-tag CI run
  [`33291029715`](https://github.com/adand-91/requirement-ledger/actions/runs/33291029715)
  passed Python 3.10–3.13 on Linux, macOS, and Windows plus the built-artefact/security smoke.
- GitHub Release:
  [`v0.2.0-alpha.1`](https://github.com/adand-91/requirement-ledger/releases/tag/v0.2.0-alpha.1).
  It is a non-draft prerelease and is not the latest stable release; `v0.1.1` remains latest.
- Public wheel SHA-256:
  `3123b30db1610e0b930c0d0f26a3a24ec3dbe47917d5da7d1f7c3b800dac615b`.
- Public sdist SHA-256:
  `1e5407f5f48d8bdd19f18749aa6bc978002415a90061426cf5bef9b40103ae05`.
- Public `SHA256SUMS` SHA-256:
  `c7f4789bc5d26fc686f49194f3da48d3426fd75c8326a1163b73edd627406011`.
- All three assets were re-downloaded from GitHub and matched the locally approved artefacts
  byte-for-byte. The downloaded checksum file verified both archives.
- The downloaded wheel and sdist installed in separate clean environments, reported
  `requirement-ledger 0.2.0a1`, and passed the deterministic Demo plus
  `review-init --mode audit` / `review-check` command chain.

## v0.2.0-alpha.2 release evidence — 2026-09-01

- Scope is the one-file, bounded `codex-scan` increment only. The version train stops after this
  release; Alpha 3, Beta, RC, and stable remain outside the current authority.
- The source suite passed all 122 tests; the dedicated envelope suite passed all nine tests.
  Compile, translation sync, and `git diff --check` also passed on macOS arm64 with Python 3.12.
- An independent security re-review closed both prior P1 findings: unaccounted records now make
  the bundle incomplete and block issue confirmation, while target/task text is absent from the
  envelope and only deterministic SHA-256 bindings remain.
- The candidate explicitly reports same-captured-byte binding as complete, concurrent path
  identity checking as metadata-best-effort, and atomic snapshot coverage as unknown. It also
  documents macOS fixed compatibility aliases, Windows' weaker reparse/identity boundary, remote
  filesystem ambiguity, and low-entropy reference linkability.
- A clean wheel install must report `requirement-ledger 0.2.0a2` and pass deterministic Demo,
  `review-init` / `review-check`, installed `codex-scan`, `0600`, privacy/canary, incomplete-source,
  and no-overwrite smokes. The extracted sdist must pass the same 122-test source suite.
- Candidate archives are built from the frozen post-checklist source snapshot. Basename-only
  SHA-256 values and command evidence live outside the source tree to avoid self-referential
  archive hashes.
- Candidate commit `c556704d19d813a9a414d011045d794dce06ef0d` passed public CI run
  `33468431105`: Python 3.10–3.13 on Linux, macOS, and Windows plus built-artefact/security smoke.
  Final release-doc commit CI, tag, Release, public-download verification, and adoption evidence
  remain pending; no programme application or promotion is claimed.
