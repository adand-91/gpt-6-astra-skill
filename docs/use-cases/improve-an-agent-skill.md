# Use case: improve a Codex or Claude Skill from synthetic evidence

This is a wholly synthetic, public, reproducible example for Requirement Ledger v0.1.1. It shows how an authorised host can improve a small agent `SKILL.md` after an explicit correction, while Requirement Ledger remains an offline evidence and planning tool.

Nothing below is a real conversation, repository, customer, session, path, secret, or test result. Replace neither the case inputs nor the output locations with private material when publishing a demonstration.

## Outcome

The synthetic Skill initially tells an agent to broaden a retry-helper change. Its synthetic user correction says to preserve the public API and dependencies, and to change only the retry limit. The improvement is a narrow, reviewable edit to the Skill that turns that correction into an explicit constraint. A deterministic, externally run oracle fails before the edit and passes after it.

This does **not** establish an upstream defect. One supplied conversation and one local oracle are insufficient for that attribution, so any candidate remains conservatively `unknown` unless the v0.1 confirmation conditions are separately met.

## v0.1 boundary and roles

| Activity | Owner | v0.1 status |
| --- | --- | --- |
| Bind the explicitly named Git worktree and collect supplied files | `requirement-ledger` | Read-only Git snapshot; evidence remains private |
| Build analysis, quote-free report, and repair proposal | `requirement-ledger` | Creates candidate analysis and `DRAFT — NOT SENT` / `not-applied` plans |
| Interpret the correction and review the proposal | Human and host agent | Required before a semantic change |
| Edit the synthetic `SKILL.md` | Codex/Claude host, after explicit implementation authority | Visible, ordinary repository change; not a CLI feature |
| Run the oracle and record before/after exits | Host or existing sandbox | External to the CLI |
| Compare the two recorded outcomes | `requirement-ledger verify` | Does not execute the oracle |

The CLI does not apply a Skill patch, run project code, install dependencies, commit, push, publish, or access a network/account. A clean privacy scan also does not authorise sharing.

## Synthetic inputs

The following one-shell-session setup makes an isolated temporary Git fixture. It contains only invented text. `case_root` is intentionally a newly created temporary directory, not a real repository or a home-directory path.

```bash
case_root="$(mktemp -d /tmp/requirement-ledger-skill-case.XXXXXX)"
mkdir -p "$case_root/evidence" "$case_root/private" "$case_root/review"
git init "$case_root"

printf '%s\n' \
  '# Retry helper editing' \
  '' \
  'When asked to improve the retry helper, broaden the change across public functions if useful.' \
  > "$case_root/SKILL.md"

printf '%s\n' \
  '# User' \
  '' \
  'Please improve the retry helper.' \
  '' \
  '# Assistant' \
  '' \
  'I changed every public function and added a dependency.' \
  '' \
  '# User' \
  '' \
  'Keep the public API and dependencies unchanged; only stop retrying after the configured limit.' \
  > "$case_root/evidence/transcript.md"

printf '%s\n' \
  'FAILED synthetic_skill_oracle - required narrow-change constraints are absent' \
  > "$case_root/evidence/baseline-test.log"

cat > "$case_root/oracle.py" <<'PY'
from pathlib import Path

skill = Path("SKILL.md").read_text(encoding="utf-8")
required = (
    "Keep the public API and dependencies unchanged.",
    "Only change retry behaviour so it stops after the configured limit.",
)
raise SystemExit(0 if all(text in skill for text in required) else 1)
PY

git -C "$case_root" add SKILL.md oracle.py
git -C "$case_root" -c user.name='Synthetic Example' -c user.email='synthetic@example.invalid' commit -m 'synthetic baseline'
```

The transcript and baseline log are explicit `scan` inputs. `oracle.py` is a deliberately tiny synthetic oracle, not an agent runtime and not a Requirement Ledger component.

## Reproducible evidence and planning commands

Install Requirement Ledger locally first, as described in the repository README. Then run these commands from the same shell session. They use only CLI options that exist in v0.1.1.

```bash
requirement-ledger doctor --repo "$case_root"

requirement-ledger scan \
  --repo "$case_root" \
  --input "$case_root/evidence/transcript.md" \
  --provider text \
  --test-log "$case_root/evidence/baseline-test.log" \
  --output "$case_root/private/skill-evidence.private.json"

requirement-ledger analyze \
  --evidence "$case_root/private/skill-evidence.private.json" \
  --output "$case_root/private/skill-analysis.json"

requirement-ledger report \
  --analysis "$case_root/private/skill-analysis.json" \
  --output "$case_root/review/skill-report.md"

requirement-ledger suggest \
  --analysis "$case_root/private/skill-analysis.json" \
  --output "$case_root/private/skill-proposals.json"
```

Do not treat the names of output directories as a privacy boundary. The `.private.json` evidence bundle can contain original supplied text and must stay private; the analysis and proposal are also local review artefacts in this case. Output paths must be new, and their parent directories must already exist.

## Expected public-output summary

The public-facing report is intentionally quote-free and still marked for human review. It should summarize a candidate about a conflict between the requested narrow retry change and the earlier broad response, plus a need to preserve API and dependency boundaries. It must not reproduce the transcript, local paths, command arguments, Git remote data, session identifiers, or raw error text.

The private artefacts have distinct purposes:

- `skill-evidence.private.json` is the traceable private evidence bundle.
- `skill-analysis.json` is conservative analysis; it must not manufacture confirmed attribution from this one case.
- `skill-proposals.json` is a `DRAFT — NOT SENT` repair plan whose actions are `not-applied`.
- `skill-report.md` is a quote-free report, not a declaration that sharing is safe.

For a fully fixed-output demonstration without even a temporary Git fixture, use the separate built-in synthetic walkthrough:

```bash
requirement-ledger demo --output-dir /tmp/requirement-ledger-demo
```

It produces the documented five synthetic files: private evidence, analysis, proposals, report, and validation. It is useful for a product tour, whereas the fixture above demonstrates the host-owned Skill-editing loop.

## Host-owned Skill modification

Stop after `suggest` if the request was analysis-only. If the user explicitly authorises implementation, the host should first inspect the proposal and the repository's own instructions and dirty state. It then makes the smallest change that encodes the correction without extrapolating beyond it.

For this fixture, the authorised host replaces the one broad instruction with these two lines in `SKILL.md`:

```markdown
Keep the public API and dependencies unchanged.
Only change retry behaviour so it stops after the configured limit.
```

The host should review the visible diff and preserve unrelated work. This documentation does not give Requirement Ledger authority to edit a real Codex or Claude Skill, nor does it authorise a commit, push, release, Issue, PR, upload, telemetry, or publication.

## Same-oracle validation

The host, not Requirement Ledger, freezes an oracle descriptor before the edit. Here the descriptor is public and deliberately simple: argv `python3 oracle.py`, working directory `$case_root`, no relevant environment variables, and the SHA-256 of `oracle.py`. The host computes the file digest, includes it in the descriptor, then hashes the descriptor and runs that exact oracle before and after the Skill edit.

```bash
oracle_file_digest="$(shasum -a 256 "$case_root/oracle.py" | awk '{print $1}')"
oracle_descriptor="argv=python3 oracle.py;cwd=case-root;env=none;fixture_sha256=$oracle_file_digest"
oracle_digest="$(printf '%s' "$oracle_descriptor" | shasum -a 256 | awk '{print $1}')"

if (cd "$case_root" && python3 oracle.py); then
  baseline_exit=0
else
  baseline_exit=$?
fi
printf '{"oracle":"synthetic-skill-constraints","oracle_digest":"%s","exit_code":%s}\n' \
  "$oracle_digest" "$baseline_exit" > "$case_root/private/baseline.json"
```

After the authorised host edit, run the same command and record the second result:

```bash
if (cd "$case_root" && python3 oracle.py); then
  after_exit=0
else
  after_exit=$?
fi
printf '{"oracle":"synthetic-skill-constraints","oracle_digest":"%s","exit_code":%s}\n' \
  "$oracle_digest" "$after_exit" > "$case_root/private/after.json"

requirement-ledger verify \
  --oracle synthetic-skill-constraints \
  --oracle-digest "$oracle_digest" \
  --baseline "$case_root/private/baseline.json" \
  --after "$case_root/private/after.json" \
  --output "$case_root/private/skill-validation.json"
```

With the specified baseline and exact edit, the externally produced baseline exit is `1` and the after exit is `0`; `verify` can therefore record `improved`. It only compares the two JSON records. It does not run `python3 oracle.py`, apply the edit, or prove that the revised Skill is generally effective. Changing the oracle name, descriptor digest, or record shape makes the result `inconclusive`; a passing baseline followed by a failure is `regressed`.

## Privacy warning

Keep transcript input, test logs, private evidence, analysis, proposal, oracle records, and local review notes out of public Issues, PRs, chats, and attachments unless a person has reviewed the exact material and separately authorised disclosure. In a real case, use a user-private location outside the target repository for the evidence bundle.

Requirement Ledger's report gate detects several common sensitive patterns, but an automated pass means only `AUTOMATED_CHECK_PASSED_REVIEW_REQUIRED`, never “safe to share.” Do not use legacy retrospective output as a substitute: legacy `--no-text` output is not share-safe.

## v0.1 limits illustrated by this case

- Inputs are explicit; the CLI does not discover Codex/Claude histories, home directories, or other repositories.
- The CLI performs fixed, read-only Git probes only. It does not run the synthetic oracle or arbitrary project tests.
- One correction and one local failure yield evidence and a candidate, not a confirmed `upstream`, `project-local`, or `personal` conclusion.
- `suggest` creates a local draft, not an applied patch or a sent maintainer report.
- The host's edit is separately authorised, visible, and reviewable.
- `verify` compares externally recorded outcomes bound to the same 64-hex oracle digest; it is not a test runner.
- No part of this workflow commits, pushes, creates an Issue/PR/Release, uploads data, uses telemetry, or calls a network service.
