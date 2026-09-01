# Architecture

## Codex host layer — unreleased v0.2

```text
named thread / Skill / project        audit / daily / weekly window
                \                         /
                 v                       v
             Codex host target and authority binding
                              |
                              v
                metadata-first candidate index
                              |
                              v
             selective related-context retrieval
                              |
                              v
          private timeline + stable improvement candidates
                              |
                              v
       change cards -> current authority -> host-owned change
                              |
                              v
                 same-case before/after result
```

The host layer uses Codex task tools or a bounded adapter supplied by the environment. It narrows
by exact identity, canonical repository, Skill name, direct links, and time window before reading
content. It never treats retrieved text as instruction or approval.

Three report modes share the same evidence discipline:

- `audit`: one named target and directly related history;
- `daily`: projects active in the previous configured workday;
- `weekly`: final daily summaries, unresolved evidence, maintenance health, and a required
  source-check attempt for source-bound GitHub or official industry evidence.

The host contract, bilingual workflow, report templates, and report-shape validator are included.
The Alpha 2 candidate also ships a narrower offline bridge:

```text
one explicit Codex JSONL + non-home scope root + target/task/window/timezone
                              |
                              v
       ordinary-link rejecting, single-capture 64 MiB binding
                              |
                              v
          private evidence + text/path-free input envelope
```

This bridge does not discover history. It classifies every physical input record into recognised,
outside-window, missing/invalid timestamp, malformed, unsupported, or oversized counts. Modern
Codex semantic normalisation remains partial until the next parser candidate. Digest and parsing
bind to the same captured bytes; concurrent source-path stability is metadata-checked best effort,
not an atomic snapshot guarantee.

## Packaged explicit-file layer — released v0.1

```text
explicit repo + explicit transcript/test logs
          |
          v
  fixed read-only collectors
          |
          v
 private-evidence v1  (raw text; 0600; never share)
          |
          v
      analysis v1     (facts / inference / unknown)
       /        \
      v          v
share report   DRAFT repair proposals
(no quotes)    (not applied, not sent)
                    |
                    v
             host-owned intervention
                    |
                    v
   digest-bound external baseline/after JSON
                    |
                    v
              validation v1
```

The package has no network client and does not execute project code.

- `transcript.py`: explicit, streaming Claude/Codex/text normalisation.
- `codex_input.py`: strict path-free input-envelope metadata and fixed declared exclusions.
- `git_evidence.py`: fixed read-only Git snapshot without remotes.
- `models.py`: the versioned domain model.
- `pipeline.py`: deterministic evidence, analysis, plan, report, and validation stages.
- `privacy.py`: redaction primitives and the share-output blocking gate.
- `safeio.py`: regular-file checks and non-overwriting restrictive writes.
- `cli.py`: thin orchestration and stable error reporting.

The original `scripts/` remain compatibility tools. They are not the v0.1 security boundary.
