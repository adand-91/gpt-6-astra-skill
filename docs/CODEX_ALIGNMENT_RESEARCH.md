# Codex alignment research

Research date: 2026-08-30. Scope: official OpenAI materials and current first-party repositories.
This note separates published facts, project decisions, and unknowns; it is not an endorsement or
programme application.

## Published facts

1. [Codex for Open Source](https://developers.openai.com/community/codex-for-oss) considers
   repository usage, ecosystem importance, active maintenance, and the applicant's maintainer
   role. Its [terms](https://learn.chatgpt.com/docs/codex-for-oss-terms) require accurate
   information and authorised repository access. OpenAI publishes no minimum Stars, Forks, or
   release count, and does not promise acceptance, timing, or a fixed benefit.
2. [Agent Skills](https://learn.chatgpt.com/docs/build-skills) are focused workflows whose
   `SKILL.md` instructions are loaded progressively. OpenAI's guidance favours explicit inputs,
   outputs, stop conditions, and unknown-state handling instead of a broad prompt that silently
   expands scope.
3. [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) instructions are
   layered from global to repository to the current directory. A nearer file wins, so evidence
   must record which instruction layer applied rather than treating every repository string as
   equal authority.
4. [Approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) keep network,
   sandbox, permission, and approval boundaries explicit. Repository text, pull-request text,
   screenshots, and tool results remain untrusted inputs; they cannot grant implementation or
   publication authority.
5. The official [`openai/skills`](https://github.com/openai/skills) repository is deprecated and
   points authors to [`openai/plugins`](https://github.com/openai/plugins) and the
   [Build Plugins guide](https://developers.openai.com/plugins/build/skills). Plugins are the
   current distribution surface, but a focused local Skill remains a valid authoring and testing
   unit.
6. The [Codex changelog](https://learn.chatgpt.com/docs/changelog) shows active work on task
   coordination, plugin configuration, MCP reliability, permissions, sandboxes, and long-thread
   history. Compatibility must therefore be fixture-driven and fail closed when a host capability
   is missing or changes shape.
7. The first-party rollout model uses typed records with a payload, timestamp, and optional
   ordinal ([history model](https://github.com/openai/codex/blob/main/codex-rs/history/src/lib.rs),
   [wire payload](https://github.com/openai/codex/blob/main/codex-rs/history/src/rollout_payload.rs)).
   The enum is evolving, so a consumer must use an allowlist and report unknown records rather
   than silently treating them as understood.
8. Current paginated rollout policy persists structured `ItemCompleted` TurnItems, while legacy
   history persists older message/tool events
   ([rollout policy](https://github.com/openai/codex/blob/main/codex-rs/rollout/src/policy.rs)).
   [`TurnItem`](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/items.rs) exposes a
   stable item ID across typed variants. `UserInput` currently includes `text`, image/local-image,
   audio/local-audio, Skill, and mention blocks; only `text` blocks are user prose
   ([user input](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/user_input.rs)).
9. The app-server history reducer upserts lifecycle snapshots by item ID and emits the latest
   state while keeping stable order
   ([thread history reducer](https://github.com/openai/codex/blob/main/codex-rs/app-server-protocol/src/protocol/thread_history.rs)).
   Requirement Ledger follows that narrow principle for `item_completed`, additionally binding
   identity to the turn so reused item IDs cannot cross turns.
10. First-party issue fixtures show real `item_completed` command records
    ([#41269](https://github.com/openai/codex/issues/41269)), mirrored response/item-completed
    messages ([#37524](https://github.com/openai/codex/issues/37524)), and a completed command
    arriving after `task_complete` ([#40041](https://github.com/openai/codex/issues/40041)). A
    terminal therefore cannot be treated as an end-of-file assertion.

## Decisions for Requirement Ledger

- Finish the offline, explicit-input Skill + CLI core before adding a plugin wrapper. The core must
  remain usable without a catalog, account connection, network client, or hosted service.
- Treat Codex task history, repository instructions, web pages, and tool output as evidence only.
  Current target-bound authority stays outside retrieved text.
- Bind one selected input by exact bytes, explicit scope root, opaque task reference, half-open
  window, timezone, and honest inclusion/exclusion metadata before normalising it.
- For the Alpha 3 adapter, preserve physical JSONL order, coalesce only structured completed-item
  snapshots by turn + item ID, let the latest valid snapshot supply status, and never infer
  completion or exclusion categories from free text.
- Encode snapshot identity as a canonical tuple, reject control-bearing IDs, fail closed on future
  or malformed user-input discriminators, and require the normalization ledger to conserve against
  recognized records. Cap both bytes and physical-record work.
- Keep structured Skill blocks out of the metadata envelope. The surrounding private evidence may
  retain selected user text and must never be shared as a public report.
- Record instruction provenance and missing-source states. Unknown or unsupported host data stops
  the affected path instead of being reported as complete.
- Qualify real maintainer-owned audit, daily, and weekly paths; synthetic tests and CI are not
  described as external adoption.
- After stable `v0.2.0`, use three distinct candidates for Skill health, before/after Skill-health
  comparison, and a Codex skill-only plugin. A version advances only when its own gate proves a
  user-visible increment.

## Unknowns and non-claims

- This research cannot predict a Codex for OSS decision or benefit amount.
- Stars and Forks may help discovery, but they do not prove maintenance quality, security, user
  success, or programme eligibility.
- Current official interfaces can evolve. Requirement Ledger does not claim universal access to
  Codex task history or identical host permissions across environments.
- The Alpha 3 allowlist is not a universal Codex parser. Unknown variants, invalid final states,
  optional-ordinal reordering, and full-thread canonical reconstruction remain explicit gaps.
- No application, Issue, pull request, tag, release, promotion, or telemetry action is authorised
  or performed by this research.
