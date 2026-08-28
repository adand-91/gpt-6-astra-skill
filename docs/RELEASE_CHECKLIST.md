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

## Public release evidence — 2026-08-28

- Final tagged commit: `ebda35154b0256395d46345e748e2be445241487`.
- Final CI run `33154303073`: all matrix and release-smoke jobs passed.
- Release: `https://github.com/adand-91/requirement-ledger/releases/tag/v0.1.0`.
- Downloaded wheel SHA-256: `34c9df440d9896c6413d663b266c764649d260975ad2856b31c6de753cbdf050`.
- Downloaded sdist SHA-256: `3c4836002c1b6660d75897b1e31ca068f87396d848ad28b75db65833a2a125fc`.
- The downloaded wheel installed with `--no-deps`, reported `requirement-ledger 0.1.0`, and
  completed the synthetic Demo.
