# CLI workflows

Use the installed command's `--help` output as the final command authority. These examples show
the v1 stable shapes and intentionally use only explicit inputs. They are entry point B,
the evidence-bound CLI review; they do not implement a Codex host-selected quick audit. A quick
audit is `host-selected / unbound`, does not call `review-init`, and cannot create a source pack,
report binding, or candidate state.

## Review scaffold

```sh
requirement-ledger review-init \
  --mode daily \
  --target TARGET \
  --at 2026-08-30T08:00:00+08:00 \
  --boundary-hour 8 \
  --timezone Asia/Shanghai \
  --output daily-review.md

requirement-ledger review-check daily-review.md
```

For v1 `audit`, supply explicit `--start`, `--end`, and `--timezone`; this is required even when a
Codex task or project was previously selected in the host. Daily/weekly modes may also use an
explicit window. Never combine `--at` with `--start`/`--end`.

## Source pack

The pack and every later input to `source-verify` must be below the same explicit non-home scope
root. Repeat `--source` for each selected file; do not build the list by directory enumeration.

```sh
requirement-ledger source-pack \
  --target TARGET \
  --scope-root SCOPE_ROOT \
  --source SOURCE_1 \
  --source SOURCE_2 \
  --output SCOPE_ROOT/sources.private.json

requirement-ledger source-verify \
  --pack SCOPE_ROOT/sources.private.json \
  --target TARGET \
  --scope-root SCOPE_ROOT \
  --source SOURCE_1 \
  --source SOURCE_2
```

Success proves only that the target digest and current bytes match the private pack.

## Candidate continuity

The host creates a strict `candidate-current/v1` private JSON object containing the SHA-256 of the
same target, `expected_head`, and exact candidate entries. On the first run, use `expected_head:
"none"`; on later runs use the prior state head exactly.

```sh
requirement-ledger candidate-sync \
  --target TARGET \
  --scope-root SCOPE_ROOT \
  --current SCOPE_ROOT/current.private.json \
  --previous SCOPE_ROOT/previous-state.private.json \
  --output SCOPE_ROOT/next-state.private.json
```

Omit `--previous` only on the first run. A stale head, target mismatch, invalid state transition,
unknown field, duplicate ID, or changed scoped file is a stop condition.

## Final report binding and identity handoff

Set a report to `status: final` only after filling its visible sections. A report claiming
`completeness: complete` needs at least one explicitly bound source and one visible `SAID:`
evidence statement. Then bind and recheck the same explicit inputs:

```sh
requirement-ledger review-bind \
  --target TARGET \
  --scope-root SCOPE_ROOT \
  --report SCOPE_ROOT/final-review.md \
  --source-pack SCOPE_ROOT/sources.private.json \
  --source SOURCE_1 \
  --candidate-state SCOPE_ROOT/candidate-state.private.json \
  --output SCOPE_ROOT/review-binding.private.json

requirement-ledger review-handoff-check \
  --binding SCOPE_ROOT/review-binding.private.json \
  --target TARGET \
  --scope-root SCOPE_ROOT \
  --report SCOPE_ROOT/final-review.md \
  --source-pack SCOPE_ROOT/sources.private.json \
  --source SOURCE_1 \
  --candidate-state SCOPE_ROOT/candidate-state.private.json
```

Repeat every `--source` exactly as used for the source pack. Success is
`REVIEW_HANDOFF_IDENTITY_READY`: current byte/state identity only, with
`authority_granted=no` and `execution=no`. An incomplete report is blocked by default; use
`--allow-incomplete-archive` only when the requested result is an explicitly incomplete archive.

## Missing capability

If evidence-bound task history is unavailable, ask for one explicit export, scope root, and exact
source files. If the CLI is missing or incompatible, report the preflight result and stop. Never
compensate by scanning the home directory or installing a package.
