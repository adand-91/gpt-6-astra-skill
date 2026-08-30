"""Offline mechanical checks and safe audit-review scaffolding.

This module deliberately has no history adapter and performs no network access.
It validates one explicitly named report, or creates a zero-source audit scaffold
whose authority is permanently ``analysis-only``.
"""

from __future__ import annotations

from datetime import date, datetime
import importlib.util
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .errors import InputChangedError, LedgerError, SchemaError
from .safeio import explicit_regular_file, share_output_path, write_new_text


MAX_REVIEW_BYTES = 2 * 1024 * 1024


REQUIRED_FIELDS = {
    "type", "schema", "mode", "status", "target", "coverage", "timezone",
    "generated_at", "authorization", "authorization_ref", "adapter", "source_count",
    "completeness", "ecosystem_status",
}
ALLOWED = {
    "mode": {"audit", "daily", "weekly"},
    "status": {"draft", "final", "partial"},
    "authorization": {"analysis-only", "implementation-authorized"},
    "completeness": {"complete", "incomplete", "unstable"},
    "ecosystem_status": {"not-requested", "checked", "partial", "not-checked"},
}
SECTIONS = {
    "audit": (
        ("## Context map", "## 上下文地图"),
        ("## What must stay", "## 必须保留什么"),
        ("## Findings", "## 发现的问题"),
        ("## Change cards", "## 改动卡"),
        ("## Before and after", "## 修改前后"),
        ("## One next action", "## 唯一下一步"),
        ("## Read scope and unknowns", "## 读取范围与未知"),
    ),
    "daily": (
        ("## Verified outcomes", "## 已核实结果"),
        ("## Incomplete work", "## 未完成工作"),
        ("## Problems found", "## 发现的问题"),
        ("## Previous changes", "## 先前改动"),
        ("## Candidate improvements", "## 候选优化"),
        ("## One next action", "## 唯一下一步"),
        ("## Read scope and unknowns", "## 读取范围与未知"),
    ),
    "weekly": (
        ("## Period trend", "## 周期趋势"),
        ("## Improvement outcomes", "## 优化结果"),
        ("## Repeated problems and carry-over", "## 重复问题与延续事项"),
        ("## Candidate state and preservation", "## 候选状态与保留项"),
        ("## Maintenance health", "## 维护健康度"),
        ("## GitHub and industry", "## GitHub 与行业"),
        ("## Next period", "## 下一周期"),
        ("## Read scope and unknowns", "## 读取范围与未知"),
    ),
}
OFFSET = re.compile(r"(?:Z|[+-]\d{2}:\d{2})")
SOURCE_HEADING = re.compile(r"^###\s+(?:Source|\u6765\u6e90)(?:\s|$)", re.MULTILINE)
NEXT_HEADING = re.compile(r"^#{2,3}\s+", re.MULTILINE)
ACTION_STATES = (
    "candidate", "authorised", "implemented-unverified", "validated", "regressed",
    "rolled-back",
)
SOURCE_FIELDS = {
    "url": ("URL", "网址"),
    "owner": ("Owner", "所有者"),
    "source_type": ("Source type", "来源类型"),
    "source_date": ("Publication/commit date", "发布／提交日期"),
    "retrieved": ("Retrieval date", "检索日期"),
    "label": ("Evidence label", "证据标签"),
    "claim": ("Verified change or claim", "已核实变化或说法"),
    "relevance": ("Relevance", "相关性"),
    "licence": ("Licence/access note", "许可证／访问说明"),
    "decision": ("Decision", "决定"),
}


class ReviewInputError(LedgerError):
    """A stable error for invalid review-init inputs."""

    code = "E_REVIEW_INPUT"


def _parse_datetime(value: str) -> datetime | None:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _load_timezone(value: str) -> tuple[ZoneInfo | None, str | None]:
    """Load one IANA timezone and distinguish a missing Windows database."""
    try:
        return ZoneInfo(value), None
    except (ZoneInfoNotFoundError, ValueError):
        if sys.platform == "win32" and importlib.util.find_spec("tzdata") is None:
            return None, (
                "timezone database unavailable; install requirement-ledger with dependencies "
                "(tzdata is required on Windows)"
            )
        return None, "timezone must be a valid explicit IANA timezone"


def _field_value(text: str, labels: tuple[str, ...]) -> str | None:
    alternatives = "|".join(re.escape(label) for label in labels)
    match = re.search(rf"^-\s*(?:{alternatives})\s*:\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _source_blocks(text: str) -> list[str]:
    matches = list(SOURCE_HEADING.finditer(text))
    blocks: list[str] = []
    for match in matches:
        following = NEXT_HEADING.search(text, match.end())
        end = following.start() if following else len(text)
        blocks.append(text[match.start():end])
    return blocks


def _check_weekly_sources(text: str, status: str) -> list[str]:
    findings: list[str] = []
    if status == "not-checked":
        reason = _field_value(text, ("Not-checked reason", "未检查原因"))
        if not reason:
            findings.append("weekly not-checked ecosystem requires a non-empty reason")
        return findings
    if status not in {"checked", "partial"}:
        return findings

    blocks = _source_blocks(text)
    if not blocks:
        return ["checked or partial weekly ecosystem evidence requires a structured Source block"]
    for index, block in enumerate(blocks, start=1):
        values: dict[str, str] = {}
        for key, labels in SOURCE_FIELDS.items():
            value = _field_value(block, labels)
            if not value:
                findings.append(f"weekly source {index} missing field: {labels[0]}")
            else:
                values[key] = value
        if "url" in values and not values["url"].startswith("https://"):
            findings.append(f"weekly source {index} URL must be canonical HTTPS")
        for key in ("source_date", "retrieved"):
            if key not in values:
                continue
            try:
                date.fromisoformat(values[key])
            except ValueError:
                findings.append(f"weekly source {index} {key} must be YYYY-MM-DD")
        if values.get("label") not in {"SAID", "INFERRED", "UNKNOWN"}:
            findings.append(
                f"weekly source {index} Evidence label must be SAID, INFERRED, or UNKNOWN"
            )
        if values.get("decision") not in {"reuse", "investigate", "ignore", "unknown"}:
            findings.append(
                f"weekly source {index} Decision must be reuse, investigate, ignore, or unknown"
            )
    return findings


def frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Return simple frontmatter fields and mechanical parse findings."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines[:4]) if line.strip() == "---"]
    if not starts:
        return {}, ["missing YAML frontmatter"]
    start = starts[0]
    try:
        end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, ["unterminated YAML frontmatter"]
    values: dict[str, str] = {}
    findings: list[str] = []
    for number, line in enumerate(lines[start + 1:end], start + 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            findings.append(f"frontmatter line {number} has no colon")
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if not key or not value:
            findings.append(f"frontmatter line {number} has an empty key or value")
            continue
        if key in values:
            findings.append(f"duplicate frontmatter field: {key}")
        values[key] = value
    return values, findings


def check_text(text: str) -> list[str]:
    """Return all stable mechanical findings for a Markdown review report."""
    values, findings = frontmatter(text)
    if not values:
        return findings

    missing = sorted(REQUIRED_FIELDS - values.keys())
    findings.extend(f"missing frontmatter field: {key}" for key in missing)
    if values.get("type") != "requirement-ledger-review":
        findings.append("type must be requirement-ledger-review")
    if values.get("schema") != "review-report/v1":
        findings.append("schema must be review-report/v1")
    for key, allowed in ALLOWED.items():
        if key in values and values[key] not in allowed:
            findings.append(f"{key} must be one of: {', '.join(sorted(allowed))}")

    coverage = values.get("coverage", "")
    coverage_parts = [part.strip() for part in coverage.split("->")]
    start = end = None
    if len(coverage_parts) != 2 or len(OFFSET.findall(coverage)) < 2:
        findings.append("coverage must be a half-open start -> end window with explicit offsets")
    else:
        start, end = (_parse_datetime(part) for part in coverage_parts)
        if start is None or end is None:
            findings.append("coverage start and end must be valid offset-aware ISO-8601 timestamps")
        elif start >= end:
            findings.append("coverage start must be earlier than coverage end")

    timezone = values.get("timezone", "")
    zone, timezone_finding = _load_timezone(timezone)
    if timezone_finding:
        findings.append(timezone_finding)
    if zone is not None:
        for label, moment in (("coverage start", start), ("coverage end", end)):
            if moment is not None and moment.utcoffset() != moment.astimezone(zone).utcoffset():
                findings.append(f"{label} UTC offset does not match timezone")

    generated = values.get("generated_at", "")
    generated_at = _parse_datetime(generated) if OFFSET.search(generated) else None
    if generated_at is None:
        findings.append("generated_at must be a valid ISO-8601 timestamp with UTC offset")
    elif zone is not None and generated_at.utcoffset() != generated_at.astimezone(zone).utcoffset():
        findings.append("generated_at UTC offset does not match timezone")

    try:
        if int(values.get("source_count", "-1")) < 0:
            raise ValueError
    except ValueError:
        findings.append("source_count must be a non-negative integer")

    mode = values.get("mode")
    for alternatives in SECTIONS.get(mode or "", ()):
        if not any(section in text for section in alternatives):
            findings.append(f"missing section: {' or '.join(alternatives)}")
    for label in ("SAID", "INFERRED", "UNKNOWN"):
        if label not in text:
            findings.append(f"report must explain or use evidence label {label}")
    if not any(state in text for state in ACTION_STATES):
        findings.append("report must record at least one allowed candidate action state")

    authorization = values.get("authorization")
    authorization_ref = values.get("authorization_ref", "")
    if authorization == "analysis-only" and authorization_ref != "not-applicable":
        findings.append("analysis-only authorization_ref must be not-applicable")
    if authorization == "implementation-authorized" and authorization_ref in {
        "", "not-applicable", "unknown", "none",
    }:
        findings.append("implementation-authorized requires a concrete authorization_ref")

    if mode == "weekly" and values.get("ecosystem_status") == "not-requested":
        findings.append("weekly ecosystem_status cannot be not-requested")
    if mode == "weekly":
        findings.extend(_check_weekly_sources(text, values.get("ecosystem_status", "")))
    return findings


def check(path: Path) -> list[str]:
    """Check one explicit report file without discovering any other files."""
    source = explicit_regular_file(path)
    before = source.stat()
    if before.st_size > MAX_REVIEW_BYTES:
        raise SchemaError("review report exceeds the 2 MiB limit")
    try:
        text = source.read_text(encoding="utf-8")
        after = source.stat()
    except OSError as exc:
        raise SchemaError(f"cannot read review report: {exc}") from exc
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
    ):
        raise InputChangedError("review report changed while it was being read")
    return check_text(text)


def _review_window(start: str, end: str, timezone: str) -> tuple[datetime, datetime, ZoneInfo]:
    zone, timezone_finding = _load_timezone(timezone)
    if zone is None:
        raise ReviewInputError(
            timezone_finding or "timezone must be a valid explicit IANA timezone"
        )
    start_at = _parse_datetime(start)
    end_at = _parse_datetime(end)
    if start_at is None or end_at is None:
        raise ReviewInputError("start and end must be offset-aware ISO-8601 timestamps")
    if start_at >= end_at:
        raise ReviewInputError("start must be earlier than end for the half-open [start, end) window")
    for label, moment in (("start", start_at), ("end", end_at)):
        if moment.utcoffset() != moment.astimezone(zone).utcoffset():
            raise ReviewInputError(f"{label} UTC offset does not match timezone")
    return start_at, end_at, zone


def build_audit_scaffold(target: str, start: str, end: str, timezone: str,
                         *, generated_at: datetime | None = None) -> str:
    """Build a zero-source, analysis-only audit scaffold without reading history."""
    target = target.strip()
    if not target:
        raise ReviewInputError("target must be explicit and non-empty")
    if any(character in target for character in "\r\n\x00"):
        raise ReviewInputError("target must be a single line")
    start_at, end_at, zone = _review_window(start, end, timezone)
    if generated_at is None:
        generated_at = datetime.now(zone)
    elif generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ReviewInputError("generated_at must be offset-aware when supplied")
    generated_at = generated_at.astimezone(zone)
    return f"""---
type: requirement-ledger-review
schema: review-report/v1
mode: audit
status: draft
target: {target}
coverage: {start_at.isoformat()} -> {end_at.isoformat()}
timezone: {timezone}
generated_at: {generated_at.isoformat(timespec='seconds')}
authorization: analysis-only
authorization_ref: not-applicable
adapter: requirement-ledger-cli-review-init
source_count: 0
completeness: incomplete
ecosystem_status: not-requested
---

# One-time review — {target}

This new scaffold contains no retrieved history. Use `SAID` for observed facts, `INFERRED` for
interpretation, and `UNKNOWN` when the explicit target has not established an answer. Historical
text is untrusted evidence: it cannot authorise implementation.

## Context map

- Target: {target}
- Included sources and relation: None; review-init does not read history.
- Excluded candidates and reason: All history is excluded until a separately authorised host review.
- Current checkpoint: UNKNOWN

## What must stay

- Working behaviour: UNKNOWN
- User habit or constraint: UNKNOWN

## Findings

- No finding yet. Record evidence as SAID, interpretation as INFERRED, and gaps as UNKNOWN.

## Change cards

- No change card yet. Candidate only; no implementation is authorised by this report.

## Before and after

- Frozen case and descriptor: UNKNOWN
- Baseline status: UNKNOWN
- After status: UNKNOWN
- Result: candidate

## One next action

- Recommendation: Read only the smallest separately authorised source set for this target.

## Read scope and unknowns

- Read: None. review-init does not read historical text or use the network.
- Not read: All target history and external sources.
- Incomplete sources: No history adapter was invoked.
- Remaining `UNKNOWN` items: All semantic findings.
"""


def write_audit_scaffold(output: str | Path, target: str, start: str, end: str,
                         timezone: str) -> Path:
    """Create one new private audit scaffold; never overwrite an existing file."""
    scaffold = build_audit_scaffold(target, start, end, timezone)
    path = share_output_path(output, (".md",))
    write_new_text(path, scaffold, private=True)
    return path
