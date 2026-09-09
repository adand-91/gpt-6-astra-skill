"""Offline mechanical checks and safe audit-review scaffolding.

This module deliberately has no history adapter and performs no network access.
It validates one explicitly named report, or creates a zero-source audit scaffold
whose authority is permanently ``analysis-only``.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone as datetime_timezone
import importlib.util
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .candidate_ledger import CandidateLedgerError, target_sha256
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
VISIBLE_H2 = re.compile(r"^\s{0,3}##(?!#)\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
MARKDOWN_CONTAINER = re.compile(
    r"^[ \t]{0,3}(?:>[ \t]?|(?:[-+*]|\d{1,9}[.)])[ \t]+)"
)
VISIBLE_SAID = re.compile(
    r"(?mi)^\s*(?:(?:[-*+]\s*)?SAID\s*:|(?:[-*+]\s*)?(?:Evidence label|证据标签)\s*[:：]\s*SAID)\s*\S"
)


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


def _remove_html_comments(line: str, in_comment: bool) -> tuple[str, bool]:
    visible: list[str] = []
    remaining = line
    while remaining:
        if in_comment:
            end = remaining.find("-->")
            if end < 0:
                return "".join(visible), True
            remaining = remaining[end + 3:]
            in_comment = False
            continue
        start = remaining.find("<!--")
        if start < 0:
            visible.append(remaining)
            break
        visible.append(remaining[:start])
        remaining = remaining[start + 4:]
        in_comment = True
    return "".join(visible), in_comment


def _without_markdown_container_prefixes(line: str) -> str:
    """Remove bounded blockquote/list prefixes before fence recognition.

    CommonMark permits fenced blocks inside list and blockquote containers.  A
    validator that only sees a fence at column 0 can therefore mistake hidden
    headings and evidence labels for visible report content.  Repeatedly
    removing syntactic container markers is deliberately conservative: it may
    exclude an ambiguous container body, but it cannot promote it to evidence.
    """
    remaining = line
    for _ in range(32):
        match = MARKDOWN_CONTAINER.match(remaining)
        if match is None:
            break
        remaining = remaining[match.end():]
    return remaining


def _visible_markdown_lines(text: str) -> list[str]:
    """Return human-visible Markdown lines outside frontmatter, comments, and fences."""

    lines = text.splitlines()
    front_start = next(
        (index for index, line in enumerate(lines[:4]) if line.strip() == "---"), None
    )
    front_end: int | None = None
    if front_start is not None:
        front_end = next(
            (index for index in range(front_start + 1, len(lines))
             if lines[index].strip() == "---"),
            None,
        )

    visible: list[str] = []
    in_comment = False
    fence_character: str | None = None
    fence_length = 0
    for index, raw_line in enumerate(lines):
        if front_start is not None and front_end is not None and front_start <= index <= front_end:
            continue
        line, in_comment = _remove_html_comments(raw_line, in_comment)
        container_line = _without_markdown_container_prefixes(line)
        stripped = container_line.lstrip()
        if fence_character is not None:
            if re.match(rf"^{re.escape(fence_character)}{{{fence_length},}}\s*$", stripped):
                fence_character = None
                fence_length = 0
            continue
        fence = FENCE.match(container_line)
        if fence:
            marker = fence.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            continue
        visible.append(line)
    return visible


def _check_visible_sections(
    mode: str,
    visible_lines: list[str],
) -> list[str]:
    findings: list[str] = []
    headings: list[tuple[int, str]] = []
    for index, line in enumerate(visible_lines):
        match = VISIBLE_H2.match(line)
        if match:
            headings.append((index, match.group(1).strip()))
    ordered_positions: list[int] = []
    for alternatives in SECTIONS.get(mode, ()):
        names = {heading.removeprefix("## ") for heading in alternatives}
        matches = [(index, name) for index, name in headings if name in names]
        if not matches:
            findings.append(f"missing section: {' or '.join(alternatives)}")
            continue
        if len(matches) > 1:
            findings.append(f"duplicate required section: {' or '.join(alternatives)}")
            continue
        ordered_positions.append(matches[0][0])
        start = matches[0][0] + 1
        end = next((index for index, _ in headings if index >= start), len(visible_lines))
        content = [line.strip() for line in visible_lines[start:end] if line.strip()]
        if not any(re.search(r"[\w\u3400-\u9fff]", line) for line in content):
            findings.append(f"required section has no visible content: {' or '.join(alternatives)}")
    if len(ordered_positions) == len(SECTIONS.get(mode, ())) and (
        ordered_positions != sorted(ordered_positions)
    ):
        findings.append(f"{mode} required sections are out of order")
    return findings


def check_text(text: str) -> list[str]:
    """Return all stable mechanical findings for a Markdown review report."""
    values, findings = frontmatter(text)
    if not values:
        return findings

    missing = sorted(REQUIRED_FIELDS - values.keys())
    findings.extend(f"missing frontmatter field: {key}" for key in missing)
    unknown = sorted(values.keys() - REQUIRED_FIELDS)
    findings.extend(f"unknown frontmatter field: {key}" for key in unknown)
    if values.get("type") != "requirement-ledger-review":
        findings.append("type must be requirement-ledger-review")
    if values.get("schema") != "review-report/v1":
        findings.append("schema must be review-report/v1")
    if "target" in values:
        try:
            target_sha256(values["target"])
        except CandidateLedgerError as exc:
            findings.append(f"target is invalid: {exc.message}")
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

    source_count = -1
    try:
        source_count = int(values.get("source_count", "-1"))
        if source_count < 0:
            raise ValueError
    except ValueError:
        findings.append("source_count must be a non-negative integer")

    mode = values.get("mode")
    visible_lines = _visible_markdown_lines(text)
    visible_text = "\n".join(visible_lines)
    findings.extend(_check_visible_sections(mode or "", visible_lines))
    for label in ("SAID", "INFERRED", "UNKNOWN"):
        if label not in visible_text:
            findings.append(f"report must explain or use evidence label {label}")
    if not any(state in visible_text for state in ACTION_STATES):
        findings.append("report must record at least one allowed candidate action state")

    if values.get("completeness") == "complete":
        if source_count <= 0:
            findings.append("complete review requires at least one explicitly bound source")
        if not VISIBLE_SAID.search(visible_text):
            findings.append("complete review requires at least one visible SAID evidence statement")
        if re.search(r"<[^>\n]{1,256}>", visible_text):
            findings.append("complete review cannot retain angle-bracket template placeholders")

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
        findings.extend(_check_weekly_sources(visible_text, values.get("ecosystem_status", "")))
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


def validate_window(start: str, end: str, timezone: str) -> tuple[datetime, datetime, ZoneInfo]:
    """Validate one explicit half-open review/input window."""
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


def _target(value: str) -> str:
    try:
        target_sha256(value)
    except CandidateLedgerError as exc:
        raise ReviewInputError(exc.message) from exc
    return value


def _boundary_hour(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 23:
        raise ReviewInputError("boundary_hour must be an integer from 0 through 23")
    return value


def _local_boundary(day: date, hour: int, zone: ZoneInfo) -> datetime:
    """Resolve a local boundary deterministically across DST gaps and overlaps.

    The first occurrence wins when a wall time is repeated.  When a wall time does not
    exist, the boundary advances to the first valid local minute.  This preserves a
    human-selected wall-clock boundary without constructing an imaginary timestamp.
    """
    requested = datetime.combine(day, time(hour=hour))
    for minute in range(181):
        wall = requested + timedelta(minutes=minute)
        candidates: list[datetime] = []
        for fold in (0, 1):
            candidate = wall.replace(tzinfo=zone, fold=fold)
            round_trip = candidate.astimezone(datetime_timezone.utc).astimezone(zone)
            if round_trip.replace(tzinfo=None) == wall and round_trip.fold == fold:
                candidates.append(candidate)
        if candidates:
            return min(candidates, key=lambda value: value.astimezone(datetime_timezone.utc))
    raise ReviewInputError("local review boundary could not be resolved within three hours")


def calculate_review_window(
    mode: str,
    timezone: str,
    *,
    boundary_hour: int = 8,
    now: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Return the last fully completed local daily or weekly half-open window."""
    if mode not in {"daily", "weekly"}:
        raise ReviewInputError("automatic review windows support only mode=daily or mode=weekly")
    zone, timezone_finding = _load_timezone(timezone)
    if zone is None:
        raise ReviewInputError(
            timezone_finding or "timezone must be a valid explicit IANA timezone"
        )
    hour = _boundary_hour(boundary_hour)
    if now is None:
        local_now = datetime.now(zone)
    elif now.tzinfo is None or now.utcoffset() is None:
        raise ReviewInputError("now must be offset-aware when supplied")
    else:
        local_now = now.astimezone(zone)

    today_boundary = _local_boundary(local_now.date(), hour, zone)
    reference_utc = local_now.astimezone(datetime_timezone.utc)
    boundary_utc = today_boundary.astimezone(datetime_timezone.utc)
    end_date = local_now.date() if reference_utc >= boundary_utc else local_now.date() - timedelta(days=1)
    end_at = _local_boundary(end_date, hour, zone)
    days = 1 if mode == "daily" else 7
    start_at = _local_boundary(end_date - timedelta(days=days), hour, zone)
    return start_at, end_at


def _scaffold_body(mode: str, target: str) -> str:
    if mode == "audit":
        return f"""# One-time review — {target}

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
    if mode == "daily":
        return f"""# Daily improvement review — {target}

This scaffold contains no retrieved history. Use `SAID` for observed facts, `INFERRED` for
interpretation, and `UNKNOWN` for unanswered questions. It is analysis-only and cannot authorise
implementation. Keep this dedicated daily layout; do not prepend the routine Jarvis project card.

## Verified outcomes

- No outcome verified yet: UNKNOWN

## Incomplete work

- No history was read; incomplete work is UNKNOWN.

## Problems found

- No finding yet. Record evidence as SAID and interpretation as INFERRED.

## Previous changes

- No previous change state was retrieved: UNKNOWN.

## Candidate improvements

- No change card yet. Candidate only; no implementation is authorised by this report.

## One next action

- Highest-value improvement for today: Read only the smallest separately authorised source set for
  this window.
- Why this one: No project history has been verified yet.
- Required authorisation: explicit access to the selected source set; implementation remains
  separately authorised.

## Read scope and unknowns

- Read: None. review-init does not read historical text or use the network.
- Not read: All sources in and outside this window.
- Excluded automated/Subagent copies: UNKNOWN.
- Incomplete sources and `UNKNOWN` items: No history adapter was invoked.
"""
    return f"""# Weekly improvement review — {target}

This scaffold contains no retrieved history or ecosystem sources. Use `SAID` for observed
facts, `INFERRED` for interpretation, and `UNKNOWN` for unanswered questions. It is analysis-only
and cannot authorise implementation. Keep this dedicated weekly layout; do not prepend the routine
Jarvis project card.

## Period trend

- No trend established: UNKNOWN.

## Improvement outcomes

- No outcome verified yet: UNKNOWN.

## Repeated problems and carry-over

- No candidate was retrieved; carry-over is UNKNOWN.

## Candidate state and preservation

- No change card yet. Candidate only; no implementation is authorised by this report.

## Maintenance health

- No maintenance evidence was read: UNKNOWN.

## GitHub and industry

- Not-checked reason: No separately authorised ecosystem source was supplied.

## Next period

1. Read only the smallest separately authorised source set for this window. Acceptance evidence:
  the next report identifies at least one visible `SAID` source or remains explicitly incomplete.
  Required authorisation: access to that selected source set.

## Read scope and unknowns

- Read: None. review-init does not read historical text or use the network.
- Not read: All sources in and outside this window.
- External sources checked/not checked: not-checked.
- Incomplete sources and remaining `UNKNOWN` items: No history adapter was invoked.
"""


def build_review_scaffold(
    mode: str,
    target: str,
    timezone: str,
    *,
    start: str | None = None,
    end: str | None = None,
    boundary_hour: int = 8,
    now: datetime | None = None,
    generated_at: datetime | None = None,
) -> str:
    """Build one zero-source, analysis-only scaffold without reading history."""
    if mode not in ALLOWED["mode"]:
        raise ReviewInputError("mode must be audit, daily, or weekly")
    target = _target(target)
    if (start is None) != (end is None):
        raise ReviewInputError("start and end must be supplied together")
    if start is not None and end is not None:
        start_at, end_at, zone = validate_window(start, end, timezone)
    elif mode == "audit":
        raise ReviewInputError("mode=audit requires explicit start and end")
    else:
        start_at, end_at = calculate_review_window(
            mode, timezone, boundary_hour=boundary_hour, now=now
        )
        zone, _ = _load_timezone(timezone)
        assert zone is not None
    if generated_at is None:
        generated_at = datetime.now(zone)
    elif generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ReviewInputError("generated_at must be offset-aware when supplied")
    generated_at = generated_at.astimezone(zone)
    ecosystem_status = "not-checked" if mode == "weekly" else "not-requested"
    return f"""---
type: requirement-ledger-review
schema: review-report/v1
mode: {mode}
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
ecosystem_status: {ecosystem_status}
---

{_scaffold_body(mode, target)}
"""


def build_audit_scaffold(target: str, start: str, end: str, timezone: str,
                         *, generated_at: datetime | None = None) -> str:
    """Build a zero-source, analysis-only audit scaffold without reading history."""
    return build_review_scaffold(
        "audit", target, timezone, start=start, end=end, generated_at=generated_at
    )


def build_daily_scaffold(
    target: str,
    timezone: str,
    *,
    start: str | None = None,
    end: str | None = None,
    boundary_hour: int = 8,
    now: datetime | None = None,
    generated_at: datetime | None = None,
) -> str:
    """Build a daily scaffold for an explicit or most recently completed local day."""
    return build_review_scaffold(
        "daily", target, timezone, start=start, end=end, boundary_hour=boundary_hour,
        now=now, generated_at=generated_at,
    )


def build_weekly_scaffold(
    target: str,
    timezone: str,
    *,
    start: str | None = None,
    end: str | None = None,
    boundary_hour: int = 8,
    now: datetime | None = None,
    generated_at: datetime | None = None,
) -> str:
    """Build a weekly scaffold for an explicit or most recently completed local week."""
    return build_review_scaffold(
        "weekly", target, timezone, start=start, end=end, boundary_hour=boundary_hour,
        now=now, generated_at=generated_at,
    )


def write_audit_scaffold(output: str | Path, target: str, start: str, end: str,
                         timezone: str) -> Path:
    """Create one new private audit scaffold; never overwrite an existing file."""
    scaffold = build_audit_scaffold(target, start, end, timezone)
    path = share_output_path(output, (".md",))
    write_new_text(path, scaffold, private=True)
    return path


def write_review_scaffold(
    output: str | Path,
    mode: str,
    target: str,
    timezone: str,
    *,
    start: str | None = None,
    end: str | None = None,
    boundary_hour: int = 8,
    now: datetime | None = None,
) -> Path:
    """Create one new private review scaffold; never overwrite an existing file."""
    scaffold = build_review_scaffold(
        mode, target, timezone, start=start, end=end, boundary_hour=boundary_hour, now=now
    )
    path = share_output_path(output, (".md",))
    write_new_text(path, scaffold, private=True)
    return path
