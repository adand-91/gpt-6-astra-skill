"""Strict metadata envelope for one explicitly selected Codex export."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from .errors import SchemaError
from .models import TOOL_VERSION
from .transcript import (CODEX_COMPLETED_ITEM_STATUSES, CODEX_COMPLETED_ITEM_TYPES,
                         CODEX_SEMANTIC_EXCLUSION_CODES)


DECLARED_EXCLUSIONS = {
    "automation": "DECLARED_AUTOMATION_NOT_SELECTED",
    "delegation": "DECLARED_DELEGATION_NOT_SELECTED",
    "subagent": "DECLARED_SUBAGENT_NOT_SELECTED",
    "system": "DECLARED_SYSTEM_NOT_SELECTED",
    "unrelated": "DECLARED_UNRELATED_TASKS_NOT_SELECTED",
    "not-provided": "DECLARED_HISTORY_NOT_PROVIDED",
}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_NORMALIZED_ID = re.compile(r"^(?:citem|cturn)_[0-9a-f]{24}$")
_WINDOW_SEMANTICS = "[start,end)"


def _reference(value: str, label: str) -> str:
    if value != value.strip() or not value or len(value) > 256:
        raise SchemaError(f"{label} must be a non-empty reference of at most 256 characters")
    if any(character in value for character in "\r\n\x00/\\") or ".." in value:
        raise SchemaError(f"{label} must be a single-line non-path reference")
    if value.startswith("~") or value.lower().startswith("file:"):
        raise SchemaError(f"{label} must not encode a local path")
    return value


def validate_codex_request(
    target: str,
    task_ref: str,
    declared_exclusions: list[str] | None,
) -> tuple[str, str, list[str]]:
    target = _reference(target, "target")
    task_ref = _reference(task_ref, "task-ref")
    exclusions = list(declared_exclusions or [])
    if len(exclusions) > len(DECLARED_EXCLUSIONS):
        raise SchemaError("too many declared exclusions")
    if len(exclusions) != len(set(exclusions)):
        raise SchemaError("declared exclusions must not repeat")
    unknown = sorted(set(exclusions) - DECLARED_EXCLUSIONS.keys())
    if unknown:
        raise SchemaError("declared exclusion is not supported")
    return target, task_ref, exclusions


def _count(value: Any, label: str, *, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaError(f"{label} must be an integer")
    if value < (1 if positive else 0):
        raise SchemaError(f"{label} is outside its allowed range")
    return value


def _aware_timestamp(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise SchemaError(f"{label} must be an offset-aware timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SchemaError(f"{label} must be an offset-aware timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SchemaError(f"{label} must be an offset-aware timestamp")
    return value


def _validated_normalization(
    value: Any,
    physical_records: int,
    recognized_records: int,
) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "schema", "parser_version", "order", "ordinary_recognized_records",
        "ordered_completed_items",
        "ordered_turn_terminals", "snapshot_dedupe", "semantic_exclusions",
        "supported_item_types",
    }:
        raise SchemaError("Codex parser did not return a valid normalization envelope")
    if (value.get("schema") != "codex-modern-normalization/v1"
            or value.get("parser_version") != "2"
            or value.get("order") != "first-physical-record-occurrence"
            or value.get("supported_item_types") != list(CODEX_COMPLETED_ITEM_TYPES)):
        raise SchemaError("Codex normalization contract is not supported")

    completed = value.get("ordered_completed_items")
    terminals = value.get("ordered_turn_terminals")
    if not isinstance(completed, list) or not isinstance(terminals, list):
        raise SchemaError("Codex normalized item lists are invalid")
    if len(completed) > 10_000 or len(terminals) > 10_000:
        raise SchemaError("Codex normalized item lists exceed their contract limit")

    safe_completed: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    previous_first = 0
    for item in completed:
        if not isinstance(item, dict) or set(item) != {
            "id", "kind", "status", "first_physical_record", "latest_physical_record",
            "first_occurred_at", "latest_occurred_at", "snapshot_count",
        }:
            raise SchemaError("Codex completed item has an invalid shape")
        item_id = item.get("id")
        kind = item.get("kind")
        status = item.get("status")
        if (not isinstance(item_id, str) or not item_id.startswith("citem_")
                or not _NORMALIZED_ID.fullmatch(item_id)
                or item_id in seen_ids or kind not in CODEX_COMPLETED_ITEM_TYPES
                or status not in CODEX_COMPLETED_ITEM_STATUSES.get(kind, ("completed",))):
            raise SchemaError("Codex completed item has invalid metadata")
        first = _count(item.get("first_physical_record"), "first physical record", positive=True)
        latest = _count(item.get("latest_physical_record"), "latest physical record", positive=True)
        snapshots = _count(item.get("snapshot_count"), "snapshot count", positive=True)
        if first < previous_first or latest < first or latest > physical_records:
            raise SchemaError("Codex completed item order is invalid")
        previous_first = first
        seen_ids.add(item_id)
        safe_completed.append({
            "id": item_id,
            "kind": kind,
            "status": status,
            "first_physical_record": first,
            "latest_physical_record": latest,
            "first_occurred_at": _aware_timestamp(item.get("first_occurred_at"), "first item time"),
            "latest_occurred_at": _aware_timestamp(item.get("latest_occurred_at"), "latest item time"),
            "snapshot_count": snapshots,
        })

    safe_terminals: list[dict[str, Any]] = []
    terminal_ids: set[str] = set()
    previous_first = 0
    for item in terminals:
        if not isinstance(item, dict) or set(item) != {
            "id", "kind", "first_physical_record", "latest_physical_record",
            "first_occurred_at", "latest_occurred_at", "snapshot_count",
        }:
            raise SchemaError("Codex turn terminal has an invalid shape")
        item_id = item.get("id")
        if (not isinstance(item_id, str) or not item_id.startswith("cturn_")
                or not _NORMALIZED_ID.fullmatch(item_id)
                or item_id in terminal_ids or item.get("kind") != "task_complete"):
            raise SchemaError("Codex turn terminal has invalid metadata")
        first = _count(item.get("first_physical_record"), "first terminal record", positive=True)
        latest = _count(item.get("latest_physical_record"), "latest terminal record", positive=True)
        snapshots = _count(item.get("snapshot_count"), "terminal snapshot count", positive=True)
        if first < previous_first or latest < first or latest > physical_records:
            raise SchemaError("Codex turn terminal order is invalid")
        previous_first = first
        terminal_ids.add(item_id)
        safe_terminals.append({
            "id": item_id,
            "kind": "task_complete",
            "first_physical_record": first,
            "latest_physical_record": latest,
            "first_occurred_at": _aware_timestamp(item.get("first_occurred_at"), "first terminal time"),
            "latest_occurred_at": _aware_timestamp(item.get("latest_occurred_at"), "latest terminal time"),
            "snapshot_count": snapshots,
        })

    dedupe = value.get("snapshot_dedupe")
    dedupe_keys = (
        "recognized_item_snapshot_records", "retained_item_snapshot_records",
        "unique_completed_items", "duplicate_item_snapshots",
        "dropped_item_snapshot_records", "recognized_turn_terminal_records",
        "retained_turn_terminal_snapshot_records", "unique_turn_terminals",
        "duplicate_turn_terminal_snapshots", "dropped_turn_terminal_snapshot_records",
        "identity", "first_position_preserved", "latest_snapshot_wins",
    )
    if not isinstance(dedupe, dict) or set(dedupe) != set(dedupe_keys):
        raise SchemaError("Codex snapshot accounting is invalid")
    safe_dedupe = {key: _count(dedupe.get(key), key) for key in dedupe_keys if key not in {
        "identity", "first_position_preserved", "latest_snapshot_wins",
    }}
    retained_item_snapshots = sum(item["snapshot_count"] for item in safe_completed)
    retained_terminal_snapshots = sum(item["snapshot_count"] for item in safe_terminals)
    if (dedupe.get("identity")
            != "sha256(canonical-json([source_sha256,turn_id,item_id]))"
            or dedupe.get("first_position_preserved") is not True
            or dedupe.get("latest_snapshot_wins") is not True
            or safe_dedupe["unique_completed_items"] != len(safe_completed)
            or safe_dedupe["unique_turn_terminals"] != len(safe_terminals)
            or safe_dedupe["retained_item_snapshot_records"] != retained_item_snapshots
            or safe_dedupe["retained_turn_terminal_snapshot_records"]
            != retained_terminal_snapshots
            or safe_dedupe["duplicate_item_snapshots"] != sum(
                item["snapshot_count"] - 1 for item in safe_completed
            )
            or safe_dedupe["duplicate_turn_terminal_snapshots"] != sum(
                item["snapshot_count"] - 1 for item in safe_terminals
            )
            or safe_dedupe["recognized_item_snapshot_records"]
            != retained_item_snapshots + safe_dedupe["dropped_item_snapshot_records"]
            or safe_dedupe["recognized_turn_terminal_records"]
            != (retained_terminal_snapshots
                + safe_dedupe["dropped_turn_terminal_snapshot_records"])):
        raise SchemaError("Codex snapshot accounting does not match normalized items")
    safe_dedupe.update({
        "identity": dedupe["identity"],
        "first_position_preserved": True,
        "latest_snapshot_wins": True,
    })

    exclusions = value.get("semantic_exclusions")
    if not isinstance(exclusions, list) or len(exclusions) != len(CODEX_SEMANTIC_EXCLUSION_CODES):
        raise SchemaError("Codex semantic exclusion accounting is invalid")
    safe_exclusions: list[dict[str, Any]] = []
    for expected, item in zip(CODEX_SEMANTIC_EXCLUSION_CODES, exclusions):
        if not isinstance(item, dict) or set(item) != {"code", "records"} or item.get("code") != expected:
            raise SchemaError("Codex semantic exclusion code is invalid")
        safe_exclusions.append({"code": expected, "records": _count(item.get("records"), expected)})

    ordinary_records = _count(
        value.get("ordinary_recognized_records"), "ordinary recognized records"
    )
    semantic_records = sum(item["records"] for item in safe_exclusions)
    if (ordinary_records + safe_dedupe["recognized_item_snapshot_records"]
            + safe_dedupe["recognized_turn_terminal_records"] + semantic_records
            != recognized_records
            or any(count > physical_records for count in (
                ordinary_records, semantic_records,
                safe_dedupe["recognized_item_snapshot_records"],
                safe_dedupe["recognized_turn_terminal_records"],
                retained_item_snapshots, retained_terminal_snapshots,
            ))):
        raise SchemaError("Codex normalization record accounting is not conserved")

    return {
        "schema": "codex-modern-normalization/v1",
        "parser_version": "2",
        "order": "first-physical-record-occurrence",
        "ordinary_recognized_records": ordinary_records,
        "ordered_completed_items": safe_completed,
        "ordered_turn_terminals": safe_terminals,
        "snapshot_dedupe": safe_dedupe,
        "semantic_exclusions": safe_exclusions,
        "supported_item_types": list(CODEX_COMPLETED_ITEM_TYPES),
    }


def build_codex_input_envelope(
    parsed: dict[str, Any],
    *,
    target: str,
    task_ref: str,
    start: datetime,
    end: datetime,
    timezone_name: str,
    declared_exclusions: list[str],
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    digest = parsed.get("digest")
    byte_count = parsed.get("bytes")
    accounting = parsed.get("accounting")
    if (not isinstance(digest, str) or not _HEX64.fullmatch(digest)
            or isinstance(byte_count, bool) or not isinstance(byte_count, int)
            or byte_count < 0 or not isinstance(accounting, dict)):
        raise SchemaError("Codex parser did not return a valid source binding")

    required_counts = {
        "physical_records", "recognized_records", "included_events",
        "outside_window_records", "missing_or_invalid_timestamp_records",
        "malformed_records", "unsupported_records", "oversized_records",
    }
    if set(accounting) != required_counts or any(
        isinstance(accounting[key], bool) or not isinstance(accounting[key], int)
        or accounting[key] < 0 for key in required_counts
    ):
        raise SchemaError("Codex parser returned invalid record accounting")
    classified = sum(accounting[key] for key in (
        "recognized_records", "outside_window_records",
        "missing_or_invalid_timestamp_records", "malformed_records",
        "unsupported_records", "oversized_records",
    ))
    if classified != accounting["physical_records"]:
        raise SchemaError("Codex record accounting is not internally balanced")
    if accounting["included_events"] > accounting["recognized_records"]:
        raise SchemaError("Codex included-event accounting exceeds recognized records")
    normalization = _validated_normalization(
        parsed.get("normalization"), accounting["physical_records"],
        accounting["recognized_records"],
    )

    exclusions = [
        {"code": "OUTSIDE_HALF_OPEN_WINDOW", "records": accounting["outside_window_records"]},
        {"code": "MISSING_OR_INVALID_TIMESTAMP", "records": accounting["missing_or_invalid_timestamp_records"]},
        {"code": "MALFORMED_RECORD", "records": accounting["malformed_records"]},
        {"code": "UNSUPPORTED_RECORD", "records": accounting["unsupported_records"]},
        {"code": "OVERSIZED_RECORD", "records": accounting["oversized_records"]},
    ]
    exclusions.extend(normalization["semantic_exclusions"])
    exclusions.extend(
        {"code": DECLARED_EXCLUSIONS[value], "records": None}
        for value in declared_exclusions
    )

    target_digest = hashlib.sha256(target.encode("utf-8")).hexdigest()
    task_digest = hashlib.sha256(task_ref.encode("utf-8")).hexdigest()
    binding = {
        "provider": "codex",
        "target_sha256": target_digest,
        "task_ref_sha256": task_digest,
        "window": {
            "semantics": _WINDOW_SEMANTICS,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "timezone": timezone_name,
        },
        "source_sha256": digest,
        "source_bytes": byte_count,
        "declared_exclusions": declared_exclusions,
    }
    envelope_id = "cenv_" + hashlib.sha256(
        json.dumps(binding, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:24]
    created = generated_at or datetime.now(timezone.utc)
    if created.tzinfo is None or created.utcoffset() is None:
        raise SchemaError("generated_at must be offset-aware")

    return {
        "schema": "codex-input-envelope/v2",
        "tool_version": TOOL_VERSION,
        "envelope_id": envelope_id,
        "created_at": created.isoformat(),
        "authority": "analysis-only",
        "provider": "codex",
        "target": {
            "id": f"target_{target_digest[:24]}",
            "reference_sha256": target_digest,
            "reference_stored": False,
        },
        "task": {
            "id": f"task_{task_digest[:24]}",
            "reference_sha256": task_digest,
            "reference_stored": False,
        },
        "window": binding["window"],
        "source": {
            "id": f"sha256:{digest}",
            "sha256": digest,
            "bytes": byte_count,
            "format": "codex-jsonl",
            "selected_by": "explicit-cli-input",
            "content_retained_in_envelope": False,
            "path_stored": False,
            "summary": {
                "physical_records": accounting["physical_records"],
                "recognized_records": accounting["recognized_records"],
                "included_events": accounting["included_events"],
                "unique_completed_items": normalization["snapshot_dedupe"]["unique_completed_items"],
                "unique_turn_terminals": normalization["snapshot_dedupe"]["unique_turn_terminals"],
            },
        },
        "inclusions": [{
            "source_id": f"sha256:{digest}",
            "relation": "explicit-selected-codex-export",
            "records": accounting["recognized_records"],
        }],
        "exclusions": exclusions,
        "normalization": normalization,
        "coverage": {
            "selected_source_set": "complete",
            "captured_bytes_binding": "complete",
            "path_identity_check": "metadata-checked-best-effort",
            "atomic_source_snapshot": "unknown",
            "physical_record_accounting": "complete",
            "semantic_normalization": "partial-alpha.3",
            "target_history": "unknown",
            "overall": "partial",
        },
        "privacy": {
            "contains_original_text": False,
            "contains_file_name": False,
            "contains_absolute_paths": False,
            "contains_raw_rollout_identifiers": False,
            "output_private_mode": "0600-where-supported",
            "output_overwrite": False,
        },
        "network_client_used": False,
        "history_discovery_performed": False,
    }
