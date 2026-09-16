# Official source register

These are audit inputs, not model-training data. Recheck URLs and dates when a new version is prepared.

| Source | Retrieved | Use | Boundary |
|---|---|---|---|
| https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra | 2026-09-16 | Short descriptions, progressive disclosure, removing obsolete handholding, contextual document reads, completion criteria, and model-specific over-constraint | Migration guidance; does not prove a local Skill will behave correctly |
| https://developers.openai.com/api/docs/guides/latest-model | 2026-09-14 | Outcome-first prompts, success criteria, tool-use precision, model baselines, and eval-driven tuning | Describes model behavior; does not prove a local Skill will behave correctly |
| https://developers.openai.com/api/docs/guides/tools-skills | 2026-09-14 | Versioned Skill bundles, `SKILL.md`, metadata triggering, limits, and Skill security | API documentation; does not authorize scanning or installing arbitrary Skills |
| https://openai.com/academy/skills/ | 2026-09-14 | Required inputs, steps, output format, final checks, composability, and review before installation | Academy guidance; does not replace project-specific acceptance |
| https://developers.openai.com/api/docs/guides/agent-builder-safety | 2026-09-14 | Untrusted input isolation, guardrails, approvals, structured data flow, and trace/eval review | Safety principles; does not authorize changing external state |
| https://developers.openai.com/api/docs/guides/evaluation-best-practices | 2026-09-14 | Early and frequent scoped evals, realistic distributions, boundary cases, logs, and human calibration | Evaluation methodology; does not prove a passing local score is production readiness |
| https://developers.openai.com/plugins/concepts/skills | 2026-09-09 | Skill name/description/instructions and optional references/assets | Plugin concepts; does not replace project-specific acceptance |
| https://developers.openai.com/plugins/app-guidelines | 2026-09-09 | Clear purpose, predictable behavior, accurate descriptions, action labels, and safety | Review guidance; does not prove public approval |
| https://developers.openai.com/plugins/deploy/submission | 2026-09-09 | Final file tree, five positive and three negative tests, release notes, and submission stages | Submission starts review; approval is separate from publication |

The optimizer should quote or paraphrase only the claim needed for the finding, retain the URL and
retrieval date, and state when a recommendation is an inference from the source.
