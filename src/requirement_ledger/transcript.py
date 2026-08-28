"""Explicit-input, event-level transcript normalisation."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Iterator

from .errors import InputChangedError, UnsafePathError
from .safeio import explicit_regular_file

MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_LINE_BYTES = 200_000
MAX_PRIVATE_TEXT = 8_000
MAX_EVENTS_PER_INPUT = 10_000
MAX_TOOL_NAME = 512

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
           until: datetime | None) -> tuple[list[dict[str, Any]], dict[str, int]]:
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
        at = _stamp(row.get("timestamp"))
        if not _inside(at, since, until):
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


def _transcript_stat_signature(info: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


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
                    or _transcript_stat_signature(path_before) != initial_signature):
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
            if (initial_signature != _transcript_stat_signature(final_fd)
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
