# Update map

The next release is `v0.2.0-beta.1` (`0.2.0b1`), adding installed daily and weekly
review scaffolds. Each release needs a real increment, a tested exact source snapshot,
and its own publication authorization. No daily release schedule is promised.

[中文更新地图](UPDATE_MAP.zh-CN.md) · [Beta 1 notes](docs/release-notes/v0.2.0-beta.1.md)

## Public baseline and current candidate

| Version | Increment | State |
| --- | --- | --- |
| v0.1.1 | Explicit evidence pipeline | Latest stable release |
| v0.2.0-alpha.1 | Named-target audit scaffold and checker | Published |
| v0.2.0-alpha.2 | Bounded explicit Codex input | Published |
| v0.2.0-alpha.3 | Supported modern Codex record normalization | Published |
| v0.2.0-beta.1 | Installed audit/daily/weekly scaffolds and local time windows | Current prerelease candidate |

## Beta 1 acceptance

- Preserve Alpha 3 commands, schemas, explicit-input boundaries, and privacy checks.
- Validate the last completed daily/seven-day windows, explicit windows, and DST transitions.
- Clean-install wheel and sdist; exercise all three review modes and failure cases.
- Pass Python 3.10–3.13 CI on Linux, macOS, and Windows before publishing.
- Publish immutable assets with checksums, then download and verify them independently.

The generated documents contain no retrieved history. A valid scaffold is not a completed review,
a scheduler, permission to edit, or proof that any finding is true.

## Later candidates

Beta 2 candidate continuity/source checks and plugin distribution, RC exact-report handoff,
and the local 1.0.0/Jarvis work remain separate future releases. They are not bundled into Beta 1.
The older ten-day plan is superseded by this capability-based sequence; a failed gate delays
publication rather than creating an empty update.
