# Astra Skill Optimizer — project application brief

## Project name

Astra Skill Optimizer

## Repository

https://github.com/adand-91/gpt-6-astra-skill

## One-line description

An open-source workflow that audits and adapts project Skills and personal workflows for GPT-6/Astra behavior, with evidence, minimal authorized changes, and reproducible validation.

## Problem

When a new model generation changes capability or interaction behavior, older Skills can become misleading: they may over-constrain the model, trigger unnecessary clarification, produce the wrong report format, or fail to verify important claims. Users need a practical way to identify that drift and update a Skill without losing safety boundaries or project context.

## Short-term objective

Use the system on selected, redacted projects to identify outdated constraints and workflow failures, propose the smallest reversible Skill changes, and compare before/after behavior with positive and boundary cases.

## Long-term vision

Build Jarvis into a personal project manager: let individuals focus on goals and direction decisions while it maintains project context, explains blockers, recommends the next action, and carries out authorized work. Skill compatibility, failure replay, evidence-backed history, and safe rollback support that long-term direction.

## Current implementation

- Independent Skill workflow for one selected project and explicitly related Skills.
- Fact, inference, and unknown states kept separate.
- Read-only audit by default; changes require explicit authorization.
- Legacy Python evidence and CLI components retained for compatibility.
- Public product display name: Astra Skill Optimizer.

## Current verification

- 223 tests were collected: 216 passed and 7 were skipped under the documented macOS boundary.
- Plugin structure validation passed.
- Translation synchronization, handoff validation, and whitespace checks passed.
- Version `1.0.3` includes a reproducible parser-regression example, scoped-authorization correction, and bilingual installation instructions. Publication is verified separately against the GitHub release.

## Why additional model access would help

A higher-capability model environment would let us evaluate the same audit workflow against harder, ambiguous, and multi-step Skill failures; compare whether proposed constraints preserve initiative and safety; and publish clearer, reproducible open-source examples. Access would be used for project research, Skill evaluation, and documentation. It would not be used for trading, customer work, credential handling, or unattended external actions.

## Open-source contribution plan

- Publish the compatibility contract and focused audit workflow.
- Add redacted failure cases and regression tests.
- Document what is verified, inferred, skipped, or unknown.
- Accept narrowly scoped community examples and improvements with reproducible tests.

## Status and request

The repository is public and MIT-licensed. GitHub reported 120 stars, 7 forks, and 4 subscribers on 2026-09-16; verified download counts are not available. This is a public project brief, not an application receipt. Application identity and submission evidence are kept outside the repository.
