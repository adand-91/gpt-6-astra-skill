"""Private, deterministic continuity state for host-supplied candidates.

This module deliberately does not read or write files and does not attempt semantic
matching.  A host owns candidate discovery and supplies an opaque identifier; this
module only validates and joins those identifiers into bounded private state.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

from .errors import SchemaError


CURRENT_SCHEMA_VERSION = "candidate-current/v1"
STATE_SCHEMA_VERSION = "candidate-ledger/v1"
MAX_TARGET_LENGTH = 512
MAX_CANDIDATES = 256
MAX_CANDIDATE_STATE_BYTES = 16 * 1024 * 1024
MAX_CANDIDATE_ID_LENGTH = 128
MAX_EVIDENCE_REFS = 32
MAX_EVIDENCE_REF_LENGTH = 512
MAX_TITLE_LENGTH = 512
MAX_DETAIL_LENGTH = 4_096
MAX_TIMESTAMP_LENGTH = 64

STATUSES = frozenset({
    "candidate", "authorised", "implemented-unverified", "validated", "regressed",
    "rolled-back",
})
UNRESOLVED_STATUSES = frozenset({
    "candidate", "authorised", "implemented-unverified", "regressed",
})
TRANSITIONS = {
    "candidate": frozenset({"candidate", "authorised"}),
    "authorised": frozenset({"authorised", "implemented-unverified"}),
    "implemented-unverified": frozenset({
        "implemented-unverified", "validated", "regressed", "rolled-back",
    }),
    "validated": frozenset({"validated", "regressed"}),
    "regressed": frozenset({"regressed", "implemented-unverified", "rolled-back"}),
    "rolled-back": frozenset({"rolled-back"}),
}

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_OPAQUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_ENTRY_FIELDS = (
    "id", "status", "title", "evidence_refs", "preserve", "smallest_change",
    "success", "boundary", "rollback", "disproof",
)
_ENTRY_FIELD_SET = frozenset(_ENTRY_FIELDS)
_STATE_ENTRY_FIELD_SET = _ENTRY_FIELD_SET | {"carried"}
_DETAIL_LIMITS = {
    "title": MAX_TITLE_LENGTH,
    "preserve": MAX_DETAIL_LENGTH,
    "smallest_change": MAX_DETAIL_LENGTH,
    "success": MAX_DETAIL_LENGTH,
    "boundary": MAX_DETAIL_LENGTH,
    "rollback": MAX_DETAIL_LENGTH,
    "disproof": MAX_DETAIL_LENGTH,
}


class CandidateLedgerError(SchemaError):
    """Stable base error for the private candidate-ledger schema."""

    code = "E_CANDIDATE_LEDGER"


class CandidateHeadError(CandidateLedgerError):
    """The supplied optimistic-concurrency head is stale or malformed."""

    code = "E_CANDIDATE_HEAD"


class CandidateTransitionError(CandidateLedgerError):
    """A candidate attempted a transition outside the frozen transition table."""

    code = "E_CANDIDATE_TRANSITION"


def target_sha256(target: str) -> str:
    """Return the only target representation permitted in persisted state."""

    if (not isinstance(target, str) or not target or target != target.strip()
            or len(target) > MAX_TARGET_LENGTH):
        raise CandidateLedgerError("target must be a non-empty string within the target limit")
    _reject_controls(target, "target")
    return hashlib.sha256(target.encode("utf-8")).hexdigest()


def _reject_controls(value: str, label: str) -> str:
    if any(
        unicodedata.category(character).startswith("C")
        or unicodedata.category(character) in {"Zl", "Zp"}
        for character in value
    ):
        raise CandidateLedgerError(f"{label} must not contain control or line-separator characters")
    return value


def _text(value: Any, label: str, maximum: int, *, non_empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum or (non_empty and not value):
        requirement = "a non-empty string" if non_empty else "a string"
        raise CandidateLedgerError(f"{label} must be {requirement} within its length limit")
    return _reject_controls(value, label)


def _hex_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _HEX64.fullmatch(value):
        raise CandidateLedgerError(f"{label} must be a lowercase SHA-256 hex digest")
    return value


def _entry(value: Any, *, state: bool) -> dict[str, Any]:
    expected = _STATE_ENTRY_FIELD_SET if state else _ENTRY_FIELD_SET
    if not isinstance(value, dict) or set(value) != expected:
        raise CandidateLedgerError("candidate entry has unknown, missing, or malformed fields")

    candidate_id = value.get("id")
    if not isinstance(candidate_id, str) or not _OPAQUE_ID.fullmatch(candidate_id):
        raise CandidateLedgerError("candidate id must be a bounded opaque identifier")
    status = value.get("status")
    if status not in STATUSES:
        raise CandidateLedgerError("candidate status is not supported")

    evidence_refs = value.get("evidence_refs")
    if not isinstance(evidence_refs, list) or len(evidence_refs) > MAX_EVIDENCE_REFS:
        raise CandidateLedgerError("candidate evidence_refs exceeds its allowed shape or limit")
    safe_refs: list[str] = []
    seen_refs: set[str] = set()
    for index, reference in enumerate(evidence_refs):
        safe_reference = _text(
            reference, f"candidate evidence_refs[{index}]", MAX_EVIDENCE_REF_LENGTH,
            non_empty=True,
        )
        if safe_reference in seen_refs:
            raise CandidateLedgerError("candidate evidence_refs must not repeat")
        seen_refs.add(safe_reference)
        safe_refs.append(safe_reference)

    safe = {
        "id": candidate_id,
        "status": status,
        "title": _text(value.get("title"), "candidate title", MAX_TITLE_LENGTH, non_empty=True),
        "evidence_refs": safe_refs,
    }
    for field, maximum in _DETAIL_LIMITS.items():
        if field == "title":
            continue
        safe[field] = _text(value.get(field), f"candidate {field}", maximum)
    if state:
        if not isinstance(value.get("carried"), bool):
            raise CandidateLedgerError("candidate carried marker must be boolean")
        if value["carried"] and status not in UNRESOLVED_STATUSES:
            raise CandidateLedgerError("only unresolved candidates may be marked as carried")
        safe["carried"] = value["carried"]
    return safe


def validate_candidate_input(value: Any) -> dict[str, Any]:
    """Validate a host's complete candidate snapshot before it enters state."""

    expected = {"schema_version", "target_sha256", "expected_head", "entries"}
    if not isinstance(value, dict) or set(value) != expected:
        raise CandidateLedgerError("candidate input has unknown, missing, or malformed fields")
    if value.get("schema_version") != CURRENT_SCHEMA_VERSION:
        raise CandidateLedgerError("candidate input schema_version is unsupported")
    target_digest = _hex_digest(value.get("target_sha256"), "candidate input target_sha256")
    expected_head = value.get("expected_head")
    if expected_head != "none":
        expected_head = _hex_digest(expected_head, "candidate input expected_head")
    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) > MAX_CANDIDATES:
        raise CandidateLedgerError("candidate input entries exceeds its allowed shape or limit")
    safe_entries = [_entry(entry, state=False) for entry in entries]
    ids = [entry["id"] for entry in safe_entries]
    if len(ids) != len(set(ids)):
        raise CandidateLedgerError("candidate input contains duplicate candidate ids")
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "target_sha256": target_digest,
        "expected_head": expected_head,
        "entries": safe_entries,
    }


def _head_payload(
    target_digest: str,
    generated_at: str,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "target_sha256": target_digest,
        "generated_at": generated_at,
        "entries": entries,
    }


def _canonical_head(
    target_digest: str,
    generated_at: str,
    entries: list[dict[str, Any]],
) -> str:
    payload = _head_payload(target_digest, generated_at, entries)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _timestamp(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TIMESTAMP_LENGTH:
        raise CandidateLedgerError("generated_at must be an offset-aware timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CandidateLedgerError("generated_at must be an offset-aware timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CandidateLedgerError("generated_at must be an offset-aware timestamp")
    canonical = parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )
    if value != canonical:
        raise CandidateLedgerError("generated_at must use canonical UTC microsecond form")
    return value


def validate_candidate_state(value: Any) -> dict[str, Any]:
    """Validate one persisted private state and its deterministic integrity head."""

    expected = {"schema_version", "target_sha256", "generated_at", "entries", "head"}
    if not isinstance(value, dict) or set(value) != expected:
        raise CandidateLedgerError("candidate state has unknown, missing, or malformed fields")
    if value.get("schema_version") != STATE_SCHEMA_VERSION:
        raise CandidateLedgerError("candidate state schema_version is unsupported")
    target_digest = _hex_digest(value.get("target_sha256"), "candidate state target_sha256")
    generated_at = _timestamp(value.get("generated_at"))
    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) > MAX_CANDIDATES:
        raise CandidateLedgerError("candidate state entries exceeds its allowed shape or limit")
    safe_entries = [_entry(entry, state=True) for entry in entries]
    ids = [entry["id"] for entry in safe_entries]
    if len(ids) != len(set(ids)) or ids != sorted(ids):
        raise CandidateLedgerError("candidate state entries must be uniquely sorted by id")
    head = _hex_digest(value.get("head"), "candidate state head")
    computed = _canonical_head(target_digest, generated_at, safe_entries)
    if not hmac.compare_digest(head, computed):
        raise CandidateHeadError("candidate state head does not bind the canonical state payload")
    safe = {
        "schema_version": STATE_SCHEMA_VERSION,
        "target_sha256": target_digest,
        "generated_at": generated_at,
        "entries": safe_entries,
        "head": head,
    }
    encoded = (json.dumps(safe, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(encoded) > MAX_CANDIDATE_STATE_BYTES:
        raise CandidateLedgerError("candidate state exceeds the 16 MiB persisted-byte limit")
    return safe


def _generated_timestamp(value: datetime | None) -> str:
    if value is None:
        value = datetime.now(timezone.utc)
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise CandidateLedgerError("generated_at must be an offset-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sync_candidate_state(
    target: str,
    current: dict[str, Any],
    previous: dict[str, Any] | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Merge one complete host snapshot into bounded private continuity state.

    The input snapshot uses an optimistic ``expected_head``.  New identifiers may
    only begin in ``candidate``.  Existing identifiers follow :data:`TRANSITIONS`.
    Missing unresolved entries are carried forward with ``carried: true``; resolved
    ``validated`` and ``rolled-back`` entries have explicit non-carry behaviour.
    """

    target_digest = target_sha256(target)
    safe_current = validate_candidate_input(current)
    if not hmac.compare_digest(safe_current["target_sha256"], target_digest):
        raise CandidateLedgerError("candidate input target does not match the requested target")

    if previous is None:
        if safe_current["expected_head"] != "none":
            raise CandidateHeadError("first candidate state must use expected_head=none")
        previous_entries: dict[str, dict[str, Any]] = {}
    else:
        safe_previous = validate_candidate_state(previous)
        if not hmac.compare_digest(safe_previous["target_sha256"], target_digest):
            raise CandidateLedgerError("previous candidate state target does not match the requested target")
        if (safe_current["expected_head"] == "none"
                or not hmac.compare_digest(safe_current["expected_head"], safe_previous["head"])):
            raise CandidateHeadError("candidate input expected_head is stale")
        previous_entries = {entry["id"]: entry for entry in safe_previous["entries"]}

    merged: dict[str, dict[str, Any]] = {}
    for current_entry in safe_current["entries"]:
        candidate_id = current_entry["id"]
        old_entry = previous_entries.get(candidate_id)
        if old_entry is None:
            if current_entry["status"] != "candidate":
                raise CandidateTransitionError("new candidates must begin in candidate status")
        elif current_entry["status"] not in TRANSITIONS[old_entry["status"]]:
            raise CandidateTransitionError(
                f"candidate {candidate_id!r} cannot transition from {old_entry['status']!r} "
                f"to {current_entry['status']!r}"
            )
        merged[candidate_id] = {**current_entry, "carried": False}

    for candidate_id, old_entry in previous_entries.items():
        if candidate_id not in merged and old_entry["status"] in UNRESOLVED_STATUSES:
            merged[candidate_id] = {**old_entry, "carried": True}

    entries = [merged[candidate_id] for candidate_id in sorted(merged)]
    timestamp = _generated_timestamp(generated_at)
    state = {
        "schema_version": STATE_SCHEMA_VERSION,
        "target_sha256": target_digest,
        "generated_at": timestamp,
        "entries": entries,
        "head": _canonical_head(target_digest, timestamp, entries),
    }
    return validate_candidate_state(state)
