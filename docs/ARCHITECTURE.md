# Architecture

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
- `git_evidence.py`: fixed read-only Git snapshot without remotes.
- `models.py`: the versioned domain model.
- `pipeline.py`: deterministic evidence, analysis, plan, report, and validation stages.
- `privacy.py`: redaction primitives and the share-output blocking gate.
- `safeio.py`: regular-file checks and non-overwriting restrictive writes.
- `cli.py`: thin orchestration and stable error reporting.

The original `scripts/` remain compatibility tools. They are not the v0.1 security boundary.
