# Astra Skill Doctor roadmap

Astra Skill Doctor is the public product and repository identity. The historical Requirement Ledger
Python core and plugin entry points remain compatibility components during migration; this roadmap
tracks Astra Skill Doctor adaptation and the longer Jarvis-like system, not a new release claim.

[中文路线图](ROADMAP.zh-CN.md) · [product completion contract](docs/V1_PRODUCT_CONTRACT.md) ·
[update map](UPDATE_MAP.md) ·
[stable contract](docs/V1_STABLE_CONTRACT.md)

## Two completion tracks

The package version and the public product experience are related but not interchangeable.

### Local technical core

```text
explicit target/window + explicit scope/files
  -> private review scaffold and checked report
  -> path-free source identity + candidate continuity
  -> exact final-report binding
  -> read-only handoff re-verification
  -> separately authorised implementation, if any
```

The historical CLI/library remains available for compatibility. The current product layer is a
focused Skill workflow for one selected project and its explicitly related Skills; it does not add
private credentials, external service dependencies, or execution authority.

`audit`, `daily`, and `weekly` are implemented modes, but they only handle the target/window/
scope/files explicitly supplied by the user or host. No mode discovers all local history.

### Astra Skill Doctor public product

The public product name is Astra Skill Doctor. Its short-term journey is to adapt existing project
Skills and workflows to GPT-6/Astra; its long-term direction is a Jarvis-like personal and
community Skill optimization system. Its v1 user journey is:

```text
one natural-language takeover
  -> bounded goal/checkpoint recovery
  -> direct, explained, or full-report answer depth
  -> one of six lifecycle scenes or a dedicated daily/weekly report
  -> separately authorised bounded progression
  -> evidence upgrade when a high-impact claim needs exact proof
  -> reliable checkpoint and handoff
```

The exact product gates are normative in [`docs/V1_PRODUCT_CONTRACT.md`](docs/V1_PRODUCT_CONTRACT.md).
The local Python `1.0.0` candidate does not, by itself, satisfy the public product gates.

## Stable promise

v1.0 guarantees conservative, offline identity handling: explicit files are checked, the final
report is bound to the selected source/candidate state, and handoff re-checks that identity. It
does not promise semantic truth, full history coverage, autonomous diagnosis, or any execution
authority.

In particular, a successful `review-handoff-check` does not authorise a code change, commit, push,
issue, release, upload, message, or public plugin submission. Incomplete evidence blocks the
normal handoff path; the explicit incomplete archive mode is retention only.

v0.1 explicit-evidence CLI workflows remain available for compatible evidence collection,
analysis, reports, suggestions, and frozen-oracle comparison.

## Release state

The local candidate is complete only after local tests, builds, clean installs, command workflows,
plugin checks, and documentation agree. It remains a local candidate until a maintainer separately
authorises and performs the external release process.

That later process includes deciding the exact commit, committing/tagging/pushing, publishing
assets, validating those public assets, and following current Codex plugin-submission requirements.
None is automated or implied by the product.

## Product sequence

1. Fast first takeover and plain-language report — complete locally.
2. Three answer depths, the full eight-field project report, and six-scene routing — implemented
   locally and awaiting final fresh-task dogfood.
3. Dedicated daily/weekly templates, strict-evidence escalation, bounded resource discovery, and
   feedback-driven improvement routing — implemented locally and awaiting the same final gate.
4. Windows/public CI, public packaging, release-time rename, and real external adoption evidence.

Step 4 requires separate external-action authorization where stated in the product contract. It is
not implied by completing an earlier local step.

## After product v1

### `1.0.x`

Ship only evidence-backed bug, security/privacy, compatibility, packaging, or documentation
repairs. No change means no release.

### `1.1`

Consider additional opt-in integrations only after their consent model, exact input boundary,
private-data retention, failure handling, and removal path are specified and tested. A new
integration must not weaken explicit source selection or introduce hidden authority.

### Later versions

Additional provider adapters and user-experience improvements can be planned from real-use
evidence. They remain out of scope until a separately authorised design establishes the security
and operational boundary.

Voice wake-up, a desktop companion, unattended night research, and broad cross-forum collection
are post-v1 ideas. They need their own runtime, privacy, failure, and resource boundaries before
implementation.
