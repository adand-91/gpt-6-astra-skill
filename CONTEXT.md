# Project context

Short pickup index. Task rules: `AGENTS.md`; product contract: `docs/GPT6_ASTRA_SKILL_CONTRACT.md`; technical handoff: `HANDOFF.md`.

## Project goal

Build **Astra Skill Doctor**: a focused system that adapts existing project Skills and workflows to new GPT-6/Astra model behavior, using traceable evidence, minimal changes, and reproducible validation. Long term it becomes a Jarvis-like personal and community Skill optimization system.

## Current checkpoint

- The public product identity is **Astra Skill Doctor**; the GitHub repository slug remains `gpt-6-astra-skill` for URL continuity.
- The independent Astra audit plugin exists at `plugins/gpt6-astra-skill-optimizer`.
- Existing Requirement Ledger package and CLI remain compatibility entry points during migration.
- Version `1.0.1` naming migration is validated and pushed to `main`: 213 tests passed, 7 skipped; translation sync and plugin validation also pass.
- Business-specific Skills and order records remain outside this project.

## Next action and boundary

Use `docs/PRO_APPLICATION_BRIEF.md` to fill the project application, then run the first redacted real-project Skill adaptation regression using the contract and compatibility map as the acceptance baseline. Do not mix in order-taking, trading, private customer records, or unrelated project implementation.
