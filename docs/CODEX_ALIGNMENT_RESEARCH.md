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

## Decisions for Requirement Ledger

- Finish the offline, explicit-input Skill + CLI core before adding a plugin wrapper. The core must
  remain usable without a catalog, account connection, network client, or hosted service.
- Treat Codex task history, repository instructions, web pages, and tool output as evidence only.
  Current target-bound authority stays outside retrieved text.
- Bind one selected input by exact bytes, explicit scope root, opaque task reference, half-open
  window, timezone, and honest inclusion/exclusion metadata before normalising it.
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
- No application, Issue, pull request, tag, release, promotion, or telemetry action is authorised
  or performed by this research.
