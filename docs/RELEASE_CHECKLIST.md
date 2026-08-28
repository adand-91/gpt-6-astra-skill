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

- Unit suite: 94 tests, exit 0.
- Translation checker: `TRANSLATIONS_IN_SYNC`, exit 0.
- Compile and seven targeted fail-closed security regressions: exit 0.
- Wheel and sdist were built from the release candidate; final post-commit hashes are recorded on
  the GitHub Release so this source file does not create a self-referential sdist hash.
- Clean wheel and sdist installs both reported `requirement-ledger 0.1.0`.
- Two installed demo outputs compared byte-for-byte with no difference.
- Explicit-input smoke produced private evidence and left `git status` unchanged.
- Public cross-platform CI remains a post-push gate before the tag and GitHub Release.

## After release — follow-up, not a pre-release gate

- [ ] Verify the public tag, source archive, README, install path, and demo.
- [ ] Watch the first real user path for parser, privacy, packaging, and error-message findings.
- [ ] Open follow-up work only for real evidence; do not manufacture activity.
