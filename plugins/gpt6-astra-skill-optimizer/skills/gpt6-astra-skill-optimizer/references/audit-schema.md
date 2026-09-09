# Audit finding schema

Each finding should be recordable in this shape:

```yaml
id: ASTRA-SKILL-001
scope: project | skill | host
severity: P0 | P1 | P2
confidence: confirmed | inferred | unknown
trigger: user-visible prompt or event
observed: concise observed behavior
expected: behavior needed for the project goal
evidence: source paths, turn/event references, or official URLs
root_cause_layer: project | skill | host/model | unresolved
astra_dimension: trigger | initiative | clarification | priority | format | tools | verification | context | authority | security | maintenance
recommendation: one bounded change
acceptance: observable positive and boundary checks
rollback: exact files or checkpoint to restore
```

Never fill `unknown` with a guess. A recommendation may be useful while its root cause remains
unresolved, but it must be labelled as such.
