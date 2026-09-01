"""Strict metadata envelope for one explicitly selected Codex export."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from .errors import SchemaError
from .models import TOOL_VERSION


DECLARED_EXCLUSIONS = {
    "automation": "DECLARED_AUTOMATION_NOT_SELECTED",
    "delegation": "DECLARED_DELEGATION_NOT_SELECTED",
    "subagent": "DECLARED_SUBAGENT_NOT_SELECTED",
    "system": "DECLARED_SYSTEM_NOT_SELECTED",
    "unrelated": "DECLARED_UNRELATED_TASKS_NOT_SELECTED",
    "not-provided": "DECLARED_HISTORY_NOT_PROVIDED",
}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
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

    exclusions = [
        {"code": "OUTSIDE_HALF_OPEN_WINDOW", "records": accounting["outside_window_records"]},
        {"code": "MISSING_OR_INVALID_TIMESTAMP", "records": accounting["missing_or_invalid_timestamp_records"]},
        {"code": "MALFORMED_RECORD", "records": accounting["malformed_records"]},
        {"code": "UNSUPPORTED_RECORD", "records": accounting["unsupported_records"]},
        {"code": "OVERSIZED_RECORD", "records": accounting["oversized_records"]},
    ]
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
        "schema": "codex-input-envelope/v1",
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
            },
        },
        "inclusions": [{
            "source_id": f"sha256:{digest}",
            "relation": "explicit-selected-codex-export",
            "records": accounting["recognized_records"],
        }],
        "exclusions": exclusions,
        "coverage": {
            "selected_source_set": "complete",
            "captured_bytes_binding": "complete",
            "path_identity_check": "metadata-checked-best-effort",
            "atomic_source_snapshot": "unknown",
            "physical_record_accounting": "complete",
            "semantic_normalization": "partial-alpha.2",
            "target_history": "unknown",
            "overall": "partial",
        },
        "privacy": {
            "contains_original_text": False,
            "contains_file_name": False,
            "contains_absolute_paths": False,
            "output_private_mode": "0600-where-supported",
            "output_overwrite": False,
        },
        "network_client_used": False,
        "history_discovery_performed": False,
    }
