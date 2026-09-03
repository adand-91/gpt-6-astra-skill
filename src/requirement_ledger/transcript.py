"""Explicit-input, event-level transcript normalisation."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Iterator

from .errors import InputChangedError, InputLimitError, UnsafePathError
from .safeio import explicit_regular_file, open_scoped_regular_input

MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_CODEX_INPUT_BYTES = 64 * 1024 * 1024
MAX_LINE_BYTES = 200_000
MAX_PRIVATE_TEXT = 8_000
MAX_EVENTS_PER_INPUT = 10_000
MAX_CODEX_RECORDS = 1_000_000
MAX_TOOL_NAME = 512
MAX_OPAQUE_SOURCE_ID = 2_048

CODEX_COMPLETED_ITEM_TYPES = (
    "UserMessage", "FunctionCallOutput", "HookPrompt", "AgentMessage", "Plan",
    "Reasoning", "CommandExecution", "DynamicToolCall", "WebSearch", "ImageView",
    "Extension", "ImageGeneration", "EnteredReviewMode", "ExitedReviewMode",
    "FileChange", "McpToolCall", "ContextCompaction",
)
CODEX_COMPLETED_ITEM_STATUSES = {
    "CommandExecution": ("completed", "failed", "declined"),
    "DynamicToolCall": ("completed", "failed"),
    "McpToolCall": ("completed", "failed"),
    "FileChange": ("completed", "failed", "declined"),
}
CODEX_USER_INPUT_BLOCK_TYPES = (
    "text", "image", "local_image", "audio", "local_audio", "skill", "mention",
)
CODEX_SEMANTIC_EXCLUSION_CODES = (
    "OBSERVED_AUTOMATION_METADATA",
    "OBSERVED_DELEGATION_RECORD",
    "OBSERVED_SUBAGENT_RECORD",
    "OBSERVED_SYSTEM_RECORD",
    "OBSERVED_NON_EVIDENCE_METADATA",
)
_CODEX_DELEGATION_EVENT_TYPES = {
    "collab_agent_spawn_begin", "collab_agent_spawn_end",
    "collab_agent_interaction_begin", "collab_agent_interaction_end",
    "collab_waiting_begin", "collab_waiting_end",
    "collab_close_begin", "collab_close_end",
    "collab_resume_begin", "collab_resume_end",
}
_CODEX_NON_EVIDENCE_EVENT_TYPES = {
    "token_count", "thread_goal_updated", "thread_rolled_back", "turn_aborted",
    "task_started", "turn_started", "thread_settings_applied",
}
_CODEX_METADATA_RECORD_TYPES = {
    "compacted", "turn_context", "world_state", "security_risk_score", "realtime_item",
}

CORRECTIONS = (
    "不对", "不是这", "不是我", "错了", "搞错", "改成", "重新", "回退", "撤销", "别再",
    "不要", "先停", "我说的是", "我要的是", "不是让你", "跑偏", "理解错", "重来",
    "that's not", "not what i", "i meant", "instead of", "wrong", "revert", "undo",
    "roll back", "rollback", "stop ", "don't ", "dont ", "start over",
)
ERROR_HINTS = (
    "error", "traceback", "exception", "command failed", "no such file", "permission denied",
    "exit code 1", "exit status 1", "fatal:", "failed",
)
TEXT_TURN = re.compile(r"^\s*(?:#{1,6}\s*)?(user|assistant|用户|助手)\s*[:：]?\s*$", re.I)


class _LimitedEvents(list[dict[str, Any]]):
    """Keep scanning after the evidence budget is exhausted, without growing memory."""

    def __init__(self) -> None:
        super().__init__()
        self.dropped = 0
        self.truncated_fields = 0

    def append(self, item: dict[str, Any]) -> None:
        if any(item.get("metadata", {}).get(flag) for flag in
               ("private_text_truncated", "tool_name_truncated")):
            self.truncated_fields += 1
        if len(self) < MAX_EVENTS_PER_INPUT:
            super().append(item)
        else:
            self.dropped += 1

    def extend(self, items: object) -> None:
        """Route bulk appends through the evidence budget as well."""

        for item in items:  # type: ignore[union-attr]
            self.append(item)


class _LimitedToolNames(dict[str, str]):
    """Bound tool-call correlation state independently of event retention."""

    def __init__(self) -> None:
        super().__init__()
        self.dropped = 0

    def remember(self, call_id: str, name: str) -> None:
        if call_id in self:
            self[call_id] = name
        elif len(self) < MAX_EVENTS_PER_INPUT:
            self[call_id] = name
        else:
            self.dropped += 1


def _stamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        got = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return got if got.tzinfo else got.replace(tzinfo=timezone.utc)


def parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    got = _stamp(value)
    if got is None:
        raise UnsafePathError("time must be an ISO-8601 timestamp with an optional offset")
    return got


def _inside(stamp: datetime | None, since: datetime | None, until: datetime | None) -> bool:
    if stamp is None:
        return since is None and until is None
    utc = stamp.astimezone(timezone.utc)
    return not ((since and utc < since.astimezone(timezone.utc)) or
                (until and utc > until.astimezone(timezone.utc)))


def _inside_half_open(stamp: datetime | None, since: datetime, until: datetime) -> bool:
    if stamp is None:
        return False
    utc = stamp.astimezone(timezone.utc)
    return not (utc < since.astimezone(timezone.utc)
                or utc >= until.astimezone(timezone.utc))


def _strict_stamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        got = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return got if got.tzinfo is not None and got.utcoffset() is not None else None


def _text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text") or block.get("content") or ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(p for p in parts if p)
    return ""


def _event(
    kind: str,
    at: datetime | None,
    text: str = "",
    *,
    text_truncated: bool = False,
    **metadata: Any,
) -> dict[str, Any]:
    normalized = text.strip()
    clipped = normalized[:MAX_PRIVATE_TEXT]
    if text_truncated or len(normalized) > MAX_PRIVATE_TEXT:
        metadata["private_text_truncated"] = True
    return {
        "kind": kind,
        "occurred_at": at.isoformat() if at else None,
        "private_text": clipped or None,
        "metadata": metadata,
    }


def _tool_name(value: Any) -> tuple[str, bool]:
    name = str(value or "unknown")
    return name[:MAX_TOOL_NAME], len(name) > MAX_TOOL_NAME


def _call_key(value: Any) -> str:
    """Keep arbitrary untrusted call identifiers out of long-lived maps."""

    return hashlib.sha256(str(value).encode("utf-8", errors="replace")).hexdigest()


def _finalize_stats(stats: dict[str, int], *collections: _LimitedEvents | _LimitedToolNames) -> None:
    stats["dropped_events"] = sum(
        collection.dropped for collection in collections if isinstance(collection, _LimitedEvents)
    )
    stats["dropped_tool_mappings"] = sum(
        collection.dropped for collection in collections if isinstance(collection, _LimitedToolNames)
    )
    stats["truncated_event_fields"] = sum(
        collection.truncated_fields for collection in collections if isinstance(collection, _LimitedEvents)
    )


def guess_provider(path: Path, handle: BinaryIO) -> str:
    if path.suffix.lower() in (".md", ".txt", ".log"):
        return "text"
    for count, (_, line) in enumerate(_input_lines(handle), start=1):
        if count > 30:
            break
        if line is None:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue
        if row.get("type") in ("event_msg", "response_item", "session_meta", "compacted"):
            return "codex"
        if row.get("type") in ("user", "assistant", "system") and "message" in row:
            return "claude"
    raise UnsafePathError("cannot determine transcript provider; pass --provider explicitly")


def _input_lines(handle: BinaryIO) -> Iterator[tuple[int, str | None]]:
    """Yield complete, size-limited logical lines without reading a giant line at once."""

    while raw := handle.readline(MAX_LINE_BYTES + 1):
        if len(raw) == MAX_LINE_BYTES + 1 and not raw.endswith(b"\n"):
            while remainder := handle.readline(MAX_LINE_BYTES + 1):
                if remainder.endswith(b"\n"):
                    break
            yield MAX_LINE_BYTES + 1, None
            continue
        size = len(raw)
        text = raw.decode("utf-8", errors="replace")
        yield (size, text) if size <= MAX_LINE_BYTES else (size, None)


def _json_lines(handle: BinaryIO) -> Iterator[tuple[int, dict[str, Any] | None]]:
    for size, raw in _input_lines(handle):
        if raw is None:
            yield size, None
            continue
        try:
            row = json.loads(raw)
        except ValueError:
            yield size, None
            continue
        yield size, row if isinstance(row, dict) else {}


def _claude(handle: BinaryIO, since: datetime | None,
            until: datetime | None) -> tuple[list[dict[str, Any]], dict[str, int]]:
    events = _LimitedEvents()
    stats = {"oversized_lines": 0, "unparsable_or_unknown_lines": 0}
    pending = _LimitedToolNames()
    for size, row in _json_lines(handle):
        if row is None:
            (stats.__setitem__("oversized_lines", stats["oversized_lines"] + 1)
             if size > MAX_LINE_BYTES else
             stats.__setitem__("unparsable_or_unknown_lines", stats["unparsable_or_unknown_lines"] + 1))
            continue
        if not row or row.get("isSidechain") or row.get("isMeta"):
            continue
        at = _stamp(row.get("timestamp"))
        if not _inside(at, since, until):
            continue
        message = row.get("message")
        if not isinstance(message, dict):
            continue
        role, content = message.get("role"), message.get("content")
        if isinstance(content, str):
            if role == "user" and row.get("type") == "user":
                events.append(_event("correction" if is_correction(content) else "user_message", at, content))
            elif role == "assistant":
                events.append(_event("assistant_message", at))
            continue
        if not isinstance(content, list):
            continue
        user_parts: list[str] = []
        had_result = False
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                user_parts.append(str(block.get("text") or ""))
            elif btype == "tool_use":
                name, name_truncated = _tool_name(block.get("name"))
                pending.remember(_call_key(block.get("id")), name)
                events.append(_event("tool_call", at, tool=name, tool_name_truncated=name_truncated))
            elif btype == "tool_result":
                had_result = True
                if block.get("is_error"):
                    events.append(_event("tool_error", at, _text(block.get("content")),
                                         tool=pending.get(_call_key(block.get("tool_use_id")), "unknown")))
        if role == "user" and not had_result:
            text = "\n".join(user_parts)
            events.append(_event("correction" if is_correction(text) else "user_message", at, text))
        elif role == "assistant":
            events.append(_event("assistant_message", at))
    _finalize_stats(stats, events, pending)
    return list(events), stats


def _codex(handle: BinaryIO, since: datetime | None,
           until: datetime | None, *,
           require_offset: bool = False,
           half_open: bool = False) -> tuple[list[dict[str, Any]], dict[str, int]]:
    events = _LimitedEvents()
    stats = {"oversized_lines": 0, "unparsable_or_unknown_lines": 0}
    calls = _LimitedToolNames()
    fallback = _LimitedEvents()
    saw_typed = False
    for size, row in _json_lines(handle):
        if row is None:
            key = "oversized_lines" if size > MAX_LINE_BYTES else "unparsable_or_unknown_lines"
            stats[key] += 1
            continue
        at = (_strict_stamp(row.get("timestamp")) if require_offset
              else _stamp(row.get("timestamp")))
        inside = (_inside_half_open(at, since, until)
                  if half_open and since is not None and until is not None
                  else _inside(at, since, until))
        if not inside:
            continue
        payload = row.get("payload")
        if not isinstance(payload, dict):
            continue
        kind, ptype = row.get("type"), payload.get("type")
        if kind == "event_msg":
            if ptype == "user_message":
                saw_typed = True
                text = str(payload.get("message") or "")
                events.append(_event("correction" if is_correction(text) else "user_message", at, text))
            elif ptype == "agent_message":
                events.append(_event("assistant_message", at))
            elif ptype == "patch_apply_end" and payload.get("success") is False:
                events.append(_event("tool_error", at, str(payload.get("stderr") or "patch failed"), tool="patch_apply"))
            continue
        if kind != "response_item":
            continue
        if ptype in ("function_call", "custom_tool_call"):
            name, name_truncated = _tool_name(payload.get("name"))
            calls.remember(_call_key(payload.get("call_id")), name)
            events.append(_event("tool_call", at, tool=name, tool_name_truncated=name_truncated))
        elif ptype in ("function_call_output", "custom_tool_call_output"):
            text = _text(payload.get("output")) or str(payload.get("output") or "")
            if looks_like_error(text):
                events.append(_event("tool_error", at, text,
                                     tool=calls.get(_call_key(payload.get("call_id")), "unknown")))
        elif ptype == "message" and payload.get("role") == "user":
            text = _text(payload.get("content"))
            fallback.append(_event("correction" if is_correction(text) else "user_message", at, text))
    if not saw_typed:
        events.extend(fallback)
    _finalize_stats(stats, events, fallback, calls)
    return list(events), stats


def _codex_accounting(
    handle: BinaryIO,
    since: datetime,
    until: datetime,
    included_events: int,
) -> dict[str, int]:
    counts = {
        "physical_records": 0,
        "recognized_records": 0,
        "included_events": included_events,
        "outside_window_records": 0,
        "missing_or_invalid_timestamp_records": 0,
        "malformed_records": 0,
        "unsupported_records": 0,
        "oversized_records": 0,
    }
    event_types = {"user_message", "agent_message", "patch_apply_end"}
    response_types = {
        "function_call", "custom_tool_call", "function_call_output",
        "custom_tool_call_output", "message",
    }
    for size, raw in _input_lines(handle):
        counts["physical_records"] += 1
        if raw is None:
            counts["oversized_records" if size > MAX_LINE_BYTES else "malformed_records"] += 1
            continue
        try:
            row = json.loads(raw)
        except ValueError:
            counts["malformed_records"] += 1
            continue
        if not isinstance(row, dict):
            counts["unsupported_records"] += 1
            continue
        at = _strict_stamp(row.get("timestamp"))
        if at is None:
            counts["missing_or_invalid_timestamp_records"] += 1
            continue
        if not _inside_half_open(at, since, until):
            counts["outside_window_records"] += 1
            continue
        payload = row.get("payload")
        if not isinstance(payload, dict):
            counts["unsupported_records"] += 1
            continue
        kind, payload_type = row.get("type"), payload.get("type")
        recognized = (
            (kind == "event_msg" and payload_type in event_types)
            or (kind == "response_item" and payload_type in response_types)
        )
        counts["recognized_records" if recognized else "unsupported_records"] += 1
    return counts


def _bounded_source_id(value: Any) -> str | None:
    if (not isinstance(value, str) or not value or len(value) > MAX_OPAQUE_SOURCE_ID
            or any(ord(character) < 32 or ord(character) == 127 for character in value)):
        return None
    return value


def _modern_user_text(item: dict[str, Any]) -> str | None:
    """Extract only official ``UserInput::Text`` blocks from a UserMessage item."""

    content = item.get("content")
    if not isinstance(content, list):
        return None
    required_text_fields = {
        "image": ("image_url",),
        "local_image": ("path",),
        "audio": ("audio_url",),
        "local_audio": ("path",),
        "skill": ("name", "path"),
        "mention": ("name", "path"),
    }
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            return None
        block_type = block.get("type")
        if block_type not in CODEX_USER_INPUT_BLOCK_TYPES:
            return None
        if block_type == "text":
            value = block.get("text")
            if (not isinstance(value, str)
                    or ("text_elements" in block
                        and not isinstance(block.get("text_elements"), list))):
                return None
            parts.append(value)
            continue
        if any(not isinstance(block.get(field), str)
               for field in required_text_fields[block_type]):
            return None
    return "".join(parts)


def _structured_source_tag(value: Any, depth: int = 0) -> str | None:
    """Read only known source discriminators; never search arbitrary metadata text."""

    if depth > 3:
        return None
    if isinstance(value, str):
        return value.lower()
    if not isinstance(value, dict):
        return None
    for key in ("type", "kind", "source", "thread_source"):
        if key in value:
            tag = _structured_source_tag(value[key], depth + 1)
            if tag is not None:
                return tag
    return None


def _completed_item_status(kind: str, item: dict[str, Any]) -> str | None:
    status = item.get("status")
    if kind in CODEX_COMPLETED_ITEM_STATUSES and kind != "FileChange":
        return (status if isinstance(status, str)
                and status in CODEX_COMPLETED_ITEM_STATUSES[kind] else None)
    if kind == "FileChange" and status is not None:
        return (status if isinstance(status, str)
                and status in CODEX_COMPLETED_ITEM_STATUSES[kind] else None)
    return "completed"


def _rollout_identity(*parts: str) -> str:
    material = json.dumps(
        list(parts), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _opaque_rollout_id(prefix: str, source_digest: str, *parts: str) -> str:
    return prefix + _rollout_identity(source_digest, *parts)[:24]


def _codex_scoped(
    handle: BinaryIO,
    since: datetime,
    until: datetime,
    source_digest: str,
) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int], dict[str, Any]]:
    """Normalize one bounded modern/legacy Codex rollout without content heuristics.

    ``item_completed`` snapshots are coalesced by ``(turn_id, item.id)``.  The
    first physical position stays fixed while the latest valid snapshot supplies
    status and message data.  Ordinary events are never content-deduplicated.
    """

    accounting = {
        "physical_records": 0,
        "recognized_records": 0,
        "included_events": 0,
        "outside_window_records": 0,
        "missing_or_invalid_timestamp_records": 0,
        "malformed_records": 0,
        "unsupported_records": 0,
        "oversized_records": 0,
    }
    stats = {
        "oversized_lines": 0,
        "unparsable_or_unknown_lines": 0,
        "dropped_events": 0,
        "dropped_tool_mappings": 0,
        "truncated_event_fields": 0,
        "dropped_item_snapshot_records": 0,
        "dropped_turn_terminal_snapshot_records": 0,
        "conflicting_item_snapshots": 0,
    }
    semantic_counts = {code: 0 for code in CODEX_SEMANTIC_EXCLUSION_CODES}
    events = _LimitedEvents()
    fallback = _LimitedEvents()
    calls = _LimitedToolNames()
    saw_typed_user = False
    completed: dict[str, dict[str, Any]] = {}
    terminals: dict[str, dict[str, Any]] = {}
    ordinary_recognized_records = 0
    recognized_item_snapshot_records = 0
    recognized_turn_terminal_records = 0
    duplicate_snapshots = 0
    duplicate_terminal_snapshots = 0

    def recognize_ordinary() -> None:
        nonlocal ordinary_recognized_records
        accounting["recognized_records"] += 1
        ordinary_recognized_records += 1

    def recognize_item_snapshot() -> None:
        nonlocal recognized_item_snapshot_records
        accounting["recognized_records"] += 1
        recognized_item_snapshot_records += 1

    def recognize_turn_terminal() -> None:
        nonlocal recognized_turn_terminal_records
        accounting["recognized_records"] += 1
        recognized_turn_terminal_records += 1

    def exclude(code: str) -> None:
        accounting["recognized_records"] += 1
        semantic_counts[code] += 1

    def append_event(target: _LimitedEvents, physical: int, event: dict[str, Any]) -> None:
        event["metadata"]["physical_record"] = physical
        target.append(event)

    for physical, (size, raw) in enumerate(_input_lines(handle), start=1):
        if physical > MAX_CODEX_RECORDS:
            raise InputLimitError(
                f"Codex input exceeds the {MAX_CODEX_RECORDS:,}-record work limit"
            )
        accounting["physical_records"] += 1
        if raw is None:
            if size > MAX_LINE_BYTES:
                accounting["oversized_records"] += 1
                stats["oversized_lines"] += 1
            else:
                accounting["malformed_records"] += 1
                stats["unparsable_or_unknown_lines"] += 1
            continue
        try:
            row = json.loads(raw)
        except ValueError:
            accounting["malformed_records"] += 1
            stats["unparsable_or_unknown_lines"] += 1
            continue
        if not isinstance(row, dict):
            accounting["unsupported_records"] += 1
            continue
        at = _strict_stamp(row.get("timestamp"))
        if at is None:
            accounting["missing_or_invalid_timestamp_records"] += 1
            continue
        if not _inside_half_open(at, since, until):
            accounting["outside_window_records"] += 1
            continue
        payload = row.get("payload")
        if not isinstance(payload, dict):
            accounting["unsupported_records"] += 1
            continue

        kind = row.get("type")
        payload_type = payload.get("type")
        if kind in ("inter_agent_communication", "inter_agent_communication_metadata"):
            exclude("OBSERVED_DELEGATION_RECORD")
            continue
        if kind == "session_meta":
            source_tag = (_structured_source_tag(payload.get("thread_source"))
                          or _structured_source_tag(payload.get("source")))
            if source_tag == "automation":
                exclude("OBSERVED_AUTOMATION_METADATA")
            elif source_tag == "subagent":
                exclude("OBSERVED_SUBAGENT_RECORD")
            else:
                exclude("OBSERVED_NON_EVIDENCE_METADATA")
            continue
        if kind in _CODEX_METADATA_RECORD_TYPES:
            exclude("OBSERVED_NON_EVIDENCE_METADATA")
            continue

        if kind == "event_msg":
            if payload_type in _CODEX_DELEGATION_EVENT_TYPES:
                exclude("OBSERVED_DELEGATION_RECORD")
                continue
            if payload_type in _CODEX_NON_EVIDENCE_EVENT_TYPES:
                exclude("OBSERVED_NON_EVIDENCE_METADATA")
                continue
            if payload_type == "sub_agent_activity":
                exclude("OBSERVED_SUBAGENT_RECORD")
                continue
            if payload_type == "user_message":
                message = payload.get("message")
                if not isinstance(message, str):
                    accounting["unsupported_records"] += 1
                    continue
                recognize_ordinary()
                saw_typed_user = True
                append_event(events, physical, _event(
                    "correction" if is_correction(message) else "user_message", at, message
                ))
                continue
            if payload_type == "agent_message":
                recognize_ordinary()
                append_event(events, physical, _event("assistant_message", at))
                continue
            if payload_type == "patch_apply_end":
                recognize_ordinary()
                if payload.get("success") is False:
                    append_event(events, physical, _event(
                        "tool_error", at, str(payload.get("stderr") or "patch failed"),
                        tool="patch_apply",
                    ))
                continue
            if payload_type in ("task_complete", "turn_complete"):
                turn_id = _bounded_source_id(payload.get("turn_id"))
                if turn_id is None:
                    accounting["unsupported_records"] += 1
                    continue
                recognize_turn_terminal()
                key = _rollout_identity(turn_id)
                existing = terminals.get(key)
                if existing is None:
                    if len(terminals) >= MAX_EVENTS_PER_INPUT:
                        stats["dropped_turn_terminal_snapshot_records"] += 1
                        continue
                    terminals[key] = {
                        "id": _opaque_rollout_id("cturn_", source_digest, turn_id),
                        "kind": "task_complete",
                        "first_physical_record": physical,
                        "latest_physical_record": physical,
                        "first_occurred_at": at.isoformat(),
                        "latest_occurred_at": at.isoformat(),
                        "snapshot_count": 1,
                    }
                else:
                    duplicate_terminal_snapshots += 1
                    existing["latest_physical_record"] = physical
                    existing["latest_occurred_at"] = at.isoformat()
                    existing["snapshot_count"] += 1
                continue
            if payload_type == "item_completed":
                turn_id = _bounded_source_id(payload.get("turn_id"))
                item = payload.get("item")
                if turn_id is None or not isinstance(item, dict):
                    accounting["unsupported_records"] += 1
                    continue
                item_id = _bounded_source_id(item.get("id"))
                item_kind = item.get("type")
                if item_id is None or not isinstance(item_kind, str):
                    accounting["unsupported_records"] += 1
                    continue
                if item_kind == "CollabAgentToolCall":
                    exclude("OBSERVED_DELEGATION_RECORD")
                    continue
                if item_kind == "SubAgentActivity":
                    exclude("OBSERVED_SUBAGENT_RECORD")
                    continue
                if item_kind not in CODEX_COMPLETED_ITEM_TYPES:
                    accounting["unsupported_records"] += 1
                    continue
                status = _completed_item_status(item_kind, item)
                if status is None:
                    accounting["unsupported_records"] += 1
                    continue
                user_text = None
                if item_kind == "UserMessage":
                    user_text = _modern_user_text(item)
                    if user_text is None:
                        accounting["unsupported_records"] += 1
                        continue
                    saw_typed_user = True
                if item_kind == "AgentMessage" and not isinstance(item.get("content"), list):
                    accounting["unsupported_records"] += 1
                    continue

                identity = _rollout_identity(turn_id, item_id)
                existing = completed.get(identity)
                if existing is not None and existing["kind"] != item_kind:
                    accounting["unsupported_records"] += 1
                    stats["conflicting_item_snapshots"] += 1
                    continue
                recognize_item_snapshot()
                if existing is None:
                    if len(completed) >= MAX_EVENTS_PER_INPUT:
                        stats["dropped_item_snapshot_records"] += 1
                        continue
                    completed[identity] = {
                        "id": _opaque_rollout_id(
                            "citem_", source_digest, turn_id, item_id
                        ),
                        "kind": item_kind,
                        "status": status,
                        "first_physical_record": physical,
                        "latest_physical_record": physical,
                        "first_occurred_at": at.isoformat(),
                        "latest_occurred_at": at.isoformat(),
                        "snapshot_count": 1,
                        "_user_text": user_text,
                    }
                else:
                    duplicate_snapshots += 1
                    existing["status"] = status
                    existing["latest_physical_record"] = physical
                    existing["latest_occurred_at"] = at.isoformat()
                    existing["snapshot_count"] += 1
                    existing["_user_text"] = user_text
                continue
            accounting["unsupported_records"] += 1
            continue

        if kind == "response_item":
            if payload_type in ("function_call", "custom_tool_call"):
                recognize_ordinary()
                name, name_truncated = _tool_name(payload.get("name"))
                calls.remember(_call_key(payload.get("call_id")), name)
                append_event(events, physical, _event(
                    "tool_call", at, tool=name, tool_name_truncated=name_truncated
                ))
                continue
            if payload_type in ("function_call_output", "custom_tool_call_output"):
                recognize_ordinary()
                text = _text(payload.get("output")) or str(payload.get("output") or "")
                if looks_like_error(text):
                    append_event(events, physical, _event(
                        "tool_error", at, text,
                        tool=calls.get(_call_key(payload.get("call_id")), "unknown"),
                    ))
                continue
            if payload_type == "message":
                role = payload.get("role")
                if role in ("system", "developer"):
                    exclude("OBSERVED_SYSTEM_RECORD")
                    continue
                if role == "user":
                    recognize_ordinary()
                    message = _text(payload.get("content"))
                    append_event(fallback, physical, _event(
                        "correction" if is_correction(message) else "user_message", at, message
                    ))
                    continue
                if role == "assistant":
                    recognize_ordinary()
                    continue
            accounting["unsupported_records"] += 1
            continue

        accounting["unsupported_records"] += 1

    modern_events = _LimitedEvents()
    for item in completed.values():
        physical = int(item["first_physical_record"])
        at = _strict_stamp(item["first_occurred_at"])
        if item["kind"] == "UserMessage":
            text = str(item.get("_user_text") or "")
            append_event(modern_events, physical, _event(
                "correction" if is_correction(text) else "user_message", at, text,
                normalized_from="item_completed",
            ))
        elif item["kind"] == "AgentMessage":
            append_event(modern_events, physical, _event(
                "assistant_message", at, normalized_from="item_completed"
            ))
        elif item["status"] in ("failed", "declined") and item["kind"] in {
            "CommandExecution", "DynamicToolCall", "McpToolCall", "FileChange",
        }:
            append_event(modern_events, physical, _event(
                "tool_error", at, tool=item["kind"],
                normalized_from="item_completed", structured_status=item["status"],
            ))

    candidates = list(events)
    if not saw_typed_user:
        candidates.extend(fallback)
    candidates.extend(modern_events)
    candidates.sort(key=lambda event: int(event.get("metadata", {}).get("physical_record", 0)))
    retained_events = candidates[:MAX_EVENTS_PER_INPUT]
    stats["dropped_events"] += (
        events.dropped + modern_events.dropped
        + (fallback.dropped if not saw_typed_user else 0)
        + max(0, len(candidates) - MAX_EVENTS_PER_INPUT)
    )
    stats["dropped_tool_mappings"] += calls.dropped
    stats["truncated_event_fields"] += (
        events.truncated_fields + modern_events.truncated_fields
        + (fallback.truncated_fields if not saw_typed_user else 0)
    )
    accounting["included_events"] = len(retained_events)

    ordered_items = []
    for item in completed.values():
        ordered_items.append({key: value for key, value in item.items() if not key.startswith("_")})
    normalization = {
        "schema": "codex-modern-normalization/v1",
        "parser_version": "2",
        "order": "first-physical-record-occurrence",
        "ordinary_recognized_records": ordinary_recognized_records,
        "ordered_completed_items": ordered_items,
        "ordered_turn_terminals": list(terminals.values()),
        "snapshot_dedupe": {
            "recognized_item_snapshot_records": recognized_item_snapshot_records,
            "retained_item_snapshot_records": sum(
                item["snapshot_count"] for item in ordered_items
            ),
            "unique_completed_items": len(ordered_items),
            "duplicate_item_snapshots": duplicate_snapshots,
            "dropped_item_snapshot_records": stats["dropped_item_snapshot_records"],
            "recognized_turn_terminal_records": recognized_turn_terminal_records,
            "retained_turn_terminal_snapshot_records": sum(
                item["snapshot_count"] for item in terminals.values()
            ),
            "unique_turn_terminals": len(terminals),
            "duplicate_turn_terminal_snapshots": duplicate_terminal_snapshots,
            "dropped_turn_terminal_snapshot_records": (
                stats["dropped_turn_terminal_snapshot_records"]
            ),
            "identity": "sha256(canonical-json([source_sha256,turn_id,item_id]))",
            "first_position_preserved": True,
            "latest_snapshot_wins": True,
        },
        "semantic_exclusions": [
            {"code": code, "records": semantic_counts[code]}
            for code in CODEX_SEMANTIC_EXCLUSION_CODES
        ],
        "supported_item_types": list(CODEX_COMPLETED_ITEM_TYPES),
    }
    return retained_events, stats, accounting, normalization


def _plain(handle: BinaryIO, since: datetime | None,
           until: datetime | None) -> tuple[list[dict[str, Any]], dict[str, int]]:
    if since or until:
        raise UnsafePathError("plain-text transcripts have no event timestamps; omit --since/--until")
    events = _LimitedEvents()
    stats = {"oversized_lines": 0, "unparsable_or_unknown_lines": 0}
    role: str | None = None
    buffer: list[str] = []
    buffer_size = 0
    buffer_truncated = False
    correction_seen = False
    correction_tail = ""
    correction_tail_size = max(len(marker) for marker in CORRECTIONS) - 1

    def append_text(line: str) -> None:
        nonlocal buffer_size, buffer_truncated, correction_seen, correction_tail
        probe = correction_tail + line
        correction_seen = correction_seen or is_correction(probe)
        correction_tail = probe[-correction_tail_size:]

        separator = 1 if buffer else 0
        remaining = MAX_PRIVATE_TEXT - buffer_size - separator
        if remaining <= 0:
            buffer_truncated = buffer_truncated or bool(line) or separator > 0
            return
        captured = line[:remaining]
        if separator:
            buffer_size += separator
        buffer.append(captured)
        buffer_size += len(captured)
        if len(captured) < len(line):
            buffer_truncated = True

    def flush() -> None:
        nonlocal buffer, buffer_size, buffer_truncated, correction_seen, correction_tail
        if not role:
            buffer = []
            buffer_size = 0
            buffer_truncated = False
            correction_seen = False
            correction_tail = ""
            return
        text = "\n".join(buffer).strip()
        if role.lower() in ("user", "用户"):
            events.append(_event("correction" if correction_seen else "user_message", None, text,
                                 text_truncated=buffer_truncated))
        else:
            events.append(_event("assistant_message", None))
        buffer = []
        buffer_size = 0
        buffer_truncated = False
        correction_seen = False
        correction_tail = ""

    for size, raw in _input_lines(handle):
        if raw is None:
            stats["oversized_lines"] += 1
            continue
        match = TEXT_TURN.match(raw)
        if match:
            flush()
            role = match.group(1)
        else:
            append_text(raw.rstrip("\n"))
    flush()
    _finalize_stats(stats, events)
    return list(events), stats


def is_correction(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in CORRECTIONS)


def looks_like_error(text: str) -> bool:
    low = text[:4000].lower()
    return any(marker in low for marker in ERROR_HINTS)


def _transcript_stat_signature(info: os.stat_result) -> tuple[int, int]:
    """Return content metadata that is stable across path and handle stats.

    File identity is checked separately with ``os.path.samestat``.  Windows can
    report different non-content mode/ctime fields for ``lstat`` and ``fstat``
    on the same file, so combining identity and content metadata caused false
    ``E_INPUT_CHANGED`` results on Python 3.12.
    """
    return (info.st_size, info.st_mtime_ns)


def parse_explicit_transcript(
    raw: str | Path,
    provider: str = "auto",
    since: str | None = None,
    until: str | None = None,
) -> dict[str, Any]:
    path = explicit_regular_file(raw)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        path_before = os.lstat(path)
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise UnsafePathError(f"cannot bind the explicit transcript: {exc}") from exc
    digest = hashlib.sha256()
    byte_count = 0
    try:
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            initial_signature = _transcript_stat_signature(opened)
            if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink > 1
                    or not os.path.samestat(path_before, opened)):
                raise InputChangedError("transcript changed before it could be bound")
            if opened.st_size > MAX_INPUT_BYTES:
                raise UnsafePathError("input exceeds the v0.1 512 MiB per-file limit")
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                byte_count += len(chunk)
                if byte_count > MAX_INPUT_BYTES:
                    raise UnsafePathError("input exceeded the v0.1 512 MiB limit while reading")
                digest.update(chunk)
            handle.seek(0)
            chosen = guess_provider(path, handle) if provider == "auto" else provider
            parser = {"claude": _claude, "codex": _codex, "text": _plain}.get(chosen)
            if parser is None:
                raise UnsafePathError("provider must be auto, claude, codex, or text")
            handle.seek(0)
            events, stats = parser(handle, parse_time(since), parse_time(until))
            final_fd = os.fstat(handle.fileno())
            path_after = os.lstat(path)
            if (not stat.S_ISREG(path_after.st_mode) or path_after.st_nlink > 1
                    or not os.path.samestat(opened, path_after)
                    or initial_signature != _transcript_stat_signature(final_fd)
                    or initial_signature != _transcript_stat_signature(path_after)):
                raise InputChangedError("input changed while it was being read")
    except (InputChangedError, UnsafePathError):
        raise
    except OSError as exc:
        raise UnsafePathError(f"cannot read the explicit transcript: {exc}") from exc
    completeness = "incomplete" if any(stats.values()) else "complete"
    return {
        "path": path,
        "digest": digest.hexdigest(),
        "bytes": byte_count,
        "provider": chosen,
        "events": events,
        "stats": stats,
        "completeness": completeness,
    }


def parse_scoped_codex_transcript(
    raw: str | Path,
    scope_root: str | Path,
    *,
    since: datetime,
    until: datetime,
) -> dict[str, Any]:
    """Read, bind, and parse one Codex export from the exact same captured bytes."""

    digest = hashlib.sha256()
    payload = bytearray()
    with open_scoped_regular_input(raw, scope_root) as bound:
        initial_signature = _transcript_stat_signature(bound.opened_stat)
        if bound.opened_stat.st_size > MAX_CODEX_INPUT_BYTES:
            raise InputLimitError("Codex input exceeds the 64 MiB limit")
        while chunk := bound.handle.read(1024 * 1024):
            payload.extend(chunk)
            if len(payload) > MAX_CODEX_INPUT_BYTES:
                raise InputLimitError("Codex input exceeded the 64 MiB limit while reading")
            digest.update(chunk)
        final_fd = os.fstat(bound.handle.fileno())
        if initial_signature != _transcript_stat_signature(final_fd):
            raise InputChangedError("Codex input changed while it was being read")

    source_digest = digest.hexdigest()
    buffer = BytesIO(payload)
    events, stats, accounting, normalization = _codex_scoped(
        buffer, since, until, source_digest
    )
    unaccounted_semantics = sum(accounting[key] for key in (
        "missing_or_invalid_timestamp_records", "malformed_records",
        "unsupported_records", "oversized_records",
    ))
    observed_semantic_exclusions = sum(
        item["records"] for item in normalization["semantic_exclusions"]
        if item["code"] != "OBSERVED_NON_EVIDENCE_METADATA"
    )
    completeness = (
        "incomplete" if (any(stats.values()) or unaccounted_semantics
                         or observed_semantic_exclusions) else "complete"
    )
    return {
        "digest": source_digest,
        "bytes": len(payload),
        "provider": "codex",
        "parser_version": "2",
        "events": events,
        "stats": stats,
        "accounting": accounting,
        "normalization": normalization,
        "completeness": completeness,
    }
