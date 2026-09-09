"""Private, deterministic source packs for explicitly selected review inputs.

This module deliberately accepts only caller-supplied files.  It neither discovers
directories nor retains paths or source bytes in the persisted pack.  File opening
and boundary checks remain owned by :func:`open_scoped_regular_input`.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections.abc import Sequence
from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .candidate_ledger import (
    MAX_CANDIDATES,
    STATE_SCHEMA_VERSION,
    CandidateLedgerError,
    target_sha256,
    validate_candidate_state,
)
from .errors import IncompleteEvidenceError, InputLimitError, LedgerError, SchemaError
from .review import ALLOWED as REVIEW_ALLOWED
from .review import MAX_REVIEW_BYTES, check_text, frontmatter, validate_window
from .safeio import open_scoped_regular_input


SOURCE_PACK_SCHEMA = "source-pack/v1"
REVIEW_BINDING_SCHEMA = "review-binding/v1"
MAX_SOURCES = 128
MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
READ_CHUNK_BYTES = 1024 * 1024
MAX_TIMESTAMP_LENGTH = 64

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_ID = re.compile(r"^src_[0-9a-f]{64}_[0-9]{3}$")
_PACK_FIELDS = frozenset({
    "schema", "target_sha256", "generated_at", "source_count", "total_bytes",
    "entries", "head", "path_stored", "content_stored", "network_used",
})
_ENTRY_FIELDS = frozenset({"source_id", "sha256", "bytes"})
_BINDING_FIELDS = frozenset({
    "schema", "target_sha256", "generated_at", "report_schema", "report_status",
    "report_mode", "coverage", "timezone", "completeness", "authorization",
    "report_sha256", "report_bytes", "source_pack_schema", "source_pack_head",
    "source_count", "total_source_bytes", "candidate_schema", "candidate_head",
    "candidate_count", "carried_count", "path_stored", "report_content_stored",
    "source_content_stored", "network_used", "authority_granted", "head",
})
_BINDING_FALSE_FIELDS = (
    "path_stored", "report_content_stored", "source_content_stored", "network_used",
    "authority_granted",
)


class SourcePackError(SchemaError):
    """A private source-pack is malformed or violates its frozen bounds."""

    code = "E_SOURCE_PACK"


class SourcePackVerificationError(SourcePackError):
    """A source-pack cannot be rebound to the supplied explicit inputs."""

    code = "E_SOURCE_PACK_VERIFY"


class ReviewBindingError(SchemaError):
    """A final review cannot be bound to the supplied explicit evidence state."""

    code = "E_REVIEW_BINDING"


class ReviewBindingVerificationError(ReviewBindingError):
    """A review binding no longer matches the explicit handoff inputs."""

    code = "E_REVIEW_BINDING_VERIFY"


def _digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _HEX64.fullmatch(value):
        raise SourcePackError(f"{label} must be a lowercase SHA-256 hex digest")
    return value


def _bounded_int(value: Any, label: str, maximum: int) -> int:
    if type(value) is not int or value < 0 or value > maximum:
        raise SourcePackError(f"{label} must be an integer within its allowed limit")
    return value


def _timestamp(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TIMESTAMP_LENGTH:
        raise SourcePackError("generated_at must be an offset-aware timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SourcePackError("generated_at must be an offset-aware timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SourcePackError("generated_at must be an offset-aware timestamp")
    canonical = parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )
    if value != canonical:
        raise SourcePackError("generated_at must use canonical UTC microsecond form")
    return value


def _generated_timestamp(value: datetime | None) -> str:
    if value is None:
        value = datetime.now(timezone.utc)
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise SourcePackError("generated_at must be an offset-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _source_id(digest: str, occurrence: int) -> str:
    return f"src_{digest}_{occurrence:03d}"


def _canonical_entries(raw_entries: list[tuple[str, int]]) -> list[dict[str, Any]]:
    """Sort digest bindings and assign an occurrence without using file identity."""

    entries: list[dict[str, Any]] = []
    occurrences: dict[str, int] = {}
    for digest, byte_count in sorted(raw_entries):
        occurrence = occurrences.get(digest, 0) + 1
        occurrences[digest] = occurrence
        entries.append({
            "source_id": _source_id(digest, occurrence),
            "sha256": digest,
            "bytes": byte_count,
        })
    return entries


def _head_payload(
    target_digest: str,
    generated_at: str,
    source_count: int,
    total_bytes: int,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SOURCE_PACK_SCHEMA,
        "target_sha256": target_digest,
        "generated_at": generated_at,
        "source_count": source_count,
        "total_bytes": total_bytes,
        "entries": entries,
        "path_stored": False,
        "content_stored": False,
        "network_used": False,
    }


def _head(
    target_digest: str,
    generated_at: str,
    source_count: int,
    total_bytes: int,
    entries: list[dict[str, Any]],
) -> str:
    payload = _head_payload(target_digest, generated_at, source_count, total_bytes, entries)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _validated(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != _PACK_FIELDS:
        raise SourcePackError("source pack has unknown, missing, or malformed fields")
    if value.get("schema") != SOURCE_PACK_SCHEMA:
        raise SourcePackError("source pack schema is unsupported")
    target_digest = _digest(value.get("target_sha256"), "source pack target_sha256")
    generated_at = _timestamp(value.get("generated_at"))
    source_count = _bounded_int(value.get("source_count"), "source_count", MAX_SOURCES)
    if source_count == 0:
        raise SourcePackError("source_count must be non-zero")
    total_bytes = _bounded_int(value.get("total_bytes"), "total_bytes", MAX_TOTAL_BYTES)
    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) != source_count:
        raise SourcePackError("source pack entries must exactly match source_count")

    raw_entries: list[tuple[str, int]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != _ENTRY_FIELDS:
            raise SourcePackError("source pack entry has unknown, missing, or malformed fields")
        source_id = entry.get("source_id")
        if not isinstance(source_id, str) or not _SOURCE_ID.fullmatch(source_id):
            raise SourcePackError(f"source pack entries[{index}].source_id is malformed")
        digest = _digest(entry.get("sha256"), f"source pack entries[{index}].sha256")
        byte_count = _bounded_int(entry.get("bytes"), f"source pack entries[{index}].bytes", MAX_SOURCE_BYTES)
        if source_id[:69] != f"src_{digest}_":
            raise SourcePackError("source pack source_id does not bind its digest")
        raw_entries.append((digest, byte_count))

    if sum(item[1] for item in raw_entries) != total_bytes:
        raise SourcePackError("source pack total_bytes does not match its entries")
    canonical_entries = _canonical_entries(raw_entries)
    if entries != canonical_entries:
        raise SourcePackError("source pack entries are not in canonical occurrence order")
    for field in ("path_stored", "content_stored", "network_used"):
        if type(value.get(field)) is not bool or value[field] is not False:
            raise SourcePackError(f"source pack {field} must be false")

    head = _digest(value.get("head"), "source pack head")
    expected_head = _head(
        target_digest, generated_at, source_count, total_bytes, canonical_entries
    )
    if not hmac.compare_digest(head, expected_head):
        raise SourcePackError("source pack head does not bind the canonical payload")
    return {
        "schema": SOURCE_PACK_SCHEMA,
        "target_sha256": target_digest,
        "generated_at": generated_at,
        "source_count": source_count,
        "total_bytes": total_bytes,
        "entries": canonical_entries,
        "head": head,
        "path_stored": False,
        "content_stored": False,
        "network_used": False,
    }


def validate_source_pack(value: dict) -> None:
    """Reject malformed, non-private, or non-canonical source-pack state."""

    _validated(value)


@contextmanager
def _open_source_inputs(
    scope_root: str | Path,
    sources: Sequence[str | Path],
) -> Iterator[list[Any]]:
    if isinstance(sources, (str, bytes)) or not isinstance(sources, Sequence):
        raise SourcePackError("sources must be an explicit sequence of file paths")
    if not sources:
        raise SourcePackError("sources must contain at least one explicit file")
    if len(sources) > MAX_SOURCES:
        raise InputLimitError("source count exceeds the 128-file limit")

    seen_physical: set[tuple[int, int]] = set()
    with ExitStack() as stack:
        bound_sources = []
        for raw in sources:
            if not isinstance(raw, (str, Path)):
                raise SourcePackError("each source must be an explicit string or Path")
            bound = stack.enter_context(open_scoped_regular_input(raw, scope_root))
            identity = (bound.opened_stat.st_dev, bound.opened_stat.st_ino)
            if identity in seen_physical:
                raise SourcePackError("sources must not repeat the same physical file")
            seen_physical.add(identity)
            if bound.opened_stat.st_size > MAX_SOURCE_BYTES:
                raise InputLimitError("source exceeds the 64 MiB per-file limit")
            bound_sources.append(bound)
        yield bound_sources


def _read_source_bindings(bound_sources: Sequence[Any]) -> list[tuple[str, int]]:
    bindings: list[tuple[str, int]] = []
    total_bytes = 0
    for bound in bound_sources:
        digest = hashlib.sha256()
        byte_count = 0
        while chunk := bound.handle.read(READ_CHUNK_BYTES):
            byte_count += len(chunk)
            if byte_count > MAX_SOURCE_BYTES:
                raise InputLimitError("source exceeded the 64 MiB limit while reading")
            total_bytes += len(chunk)
            if total_bytes > MAX_TOTAL_BYTES:
                raise InputLimitError("sources exceeded the 256 MiB total limit while reading")
            digest.update(chunk)
        bindings.append((digest.hexdigest(), byte_count))
    return bindings


def _source_bindings(
    scope_root: str | Path,
    sources: Sequence[str | Path],
) -> list[tuple[str, int]]:
    with _open_source_inputs(scope_root, sources) as bound_sources:
        return _read_source_bindings(bound_sources)


def _source_pack_from_bindings(
    target_digest: str,
    raw_entries: list[tuple[str, int]],
    generated_at: datetime | None,
) -> dict[str, Any]:
    entries = _canonical_entries(raw_entries)
    timestamp = _generated_timestamp(generated_at)
    pack = {
        "schema": SOURCE_PACK_SCHEMA,
        "target_sha256": target_digest,
        "generated_at": timestamp,
        "source_count": len(entries),
        "total_bytes": sum(byte_count for _, byte_count in raw_entries),
        "entries": entries,
        "head": _head(
            target_digest,
            timestamp,
            len(entries),
            sum(byte_count for _, byte_count in raw_entries),
            entries,
        ),
        "path_stored": False,
        "content_stored": False,
        "network_used": False,
    }
    validate_source_pack(pack)
    return pack


def build_source_pack(
    target: str,
    scope_root: str | Path,
    sources: Sequence[str | Path],
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a path-free digest pack from caller-selected, scoped regular files."""

    try:
        target_digest = target_sha256(target)
    except CandidateLedgerError as exc:
        raise SourcePackError(exc.message) from exc
    raw_entries = _source_bindings(scope_root, sources)
    return _source_pack_from_bindings(target_digest, raw_entries, generated_at)


def _verify_source_pack_bindings(
    value: dict,
    target: str,
    raw_entries: list[tuple[str, int]],
) -> dict[str, Any]:
    expected = _validated(value)
    try:
        target_digest = target_sha256(target)
    except CandidateLedgerError as exc:
        raise SourcePackVerificationError(exc.message) from exc
    generated_at = datetime.fromisoformat(expected["generated_at"].replace("Z", "+00:00"))
    current = _source_pack_from_bindings(target_digest, raw_entries, generated_at)
    stable_fields = (
        "schema", "target_sha256", "generated_at", "source_count", "total_bytes", "entries", "head",
        "path_stored", "content_stored", "network_used",
    )
    if any(current[field] != expected[field] for field in stable_fields):
        raise SourcePackVerificationError(
            "source pack does not match the currently rebound target and explicit sources"
        )
    return expected


def verify_source_pack(
    value: dict,
    target: str,
    scope_root: str | Path,
    sources: Sequence[str | Path],
) -> dict[str, Any]:
    """Rebind every selected input and reject any stable-field mismatch.

    Success establishes only that the current named files and target digest match
    this pack.  It does not establish authorship, truth, freshness, or authority.
    """

    raw_entries = _source_bindings(scope_root, sources)
    return _verify_source_pack_bindings(value, target, raw_entries)


def _binding_timestamp(value: Any) -> str:
    try:
        return _timestamp(value)
    except SourcePackError as exc:
        raise ReviewBindingError(exc.message) from exc


def _binding_digest(value: Any, label: str) -> str:
    try:
        return _digest(value, label)
    except SourcePackError as exc:
        raise ReviewBindingError(exc.message) from exc


def _binding_string(value: Any, label: str, *, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ReviewBindingError(f"{label} must be a non-empty bounded string")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ReviewBindingError(f"{label} must not contain control characters")
    return value


def _binding_int(value: Any, label: str, maximum: int, *, nonzero: bool = False) -> int:
    if type(value) is not int or value < (1 if nonzero else 0) or value > maximum:
        raise ReviewBindingError(f"{label} must be an integer within its allowed limit")
    return value


def _binding_stable_payload(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value[key]
        for key in sorted(_BINDING_FIELDS - {"head"})
    }


def _binding_head(value: dict[str, Any]) -> str:
    encoded = json.dumps(
        _binding_stable_payload(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _validated_binding(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != _BINDING_FIELDS:
        raise ReviewBindingError("review binding has unknown, missing, or malformed fields")
    if value.get("schema") != REVIEW_BINDING_SCHEMA:
        raise ReviewBindingError("review binding schema is unsupported")
    target_digest = _binding_digest(value.get("target_sha256"), "review binding target_sha256")
    generated_at = _binding_timestamp(value.get("generated_at"))
    if value.get("report_schema") != "review-report/v1":
        raise ReviewBindingError("review binding report_schema is unsupported")
    if value.get("report_status") != "final":
        raise ReviewBindingError("review binding report_status must be final")
    report_mode = value.get("report_mode")
    if report_mode not in REVIEW_ALLOWED["mode"]:
        raise ReviewBindingError("review binding report_mode is unsupported")
    coverage = _binding_string(value.get("coverage"), "review binding coverage")
    timezone_name = _binding_string(value.get("timezone"), "review binding timezone", maximum=128)
    parts = [part.strip() for part in coverage.split("->")]
    if len(parts) != 2:
        raise ReviewBindingError("review binding coverage must contain one half-open window")
    try:
        validate_window(parts[0], parts[1], timezone_name)
    except LedgerError as exc:
        raise ReviewBindingError(f"review binding coverage is invalid: {exc.message}") from exc
    completeness = value.get("completeness")
    if completeness not in REVIEW_ALLOWED["completeness"]:
        raise ReviewBindingError("review binding completeness is unsupported")
    authorization = value.get("authorization")
    if authorization not in REVIEW_ALLOWED["authorization"]:
        raise ReviewBindingError("review binding authorization is unsupported")
    report_digest = _binding_digest(value.get("report_sha256"), "review binding report_sha256")
    report_bytes = _binding_int(
        value.get("report_bytes"), "review binding report_bytes", MAX_REVIEW_BYTES, nonzero=True
    )
    if value.get("source_pack_schema") != SOURCE_PACK_SCHEMA:
        raise ReviewBindingError("review binding source_pack_schema is unsupported")
    source_pack_head = _binding_digest(
        value.get("source_pack_head"), "review binding source_pack_head"
    )
    source_count = _binding_int(
        value.get("source_count"), "review binding source_count", MAX_SOURCES, nonzero=True
    )
    total_source_bytes = _binding_int(
        value.get("total_source_bytes"), "review binding total_source_bytes", MAX_TOTAL_BYTES
    )
    if value.get("candidate_schema") != STATE_SCHEMA_VERSION:
        raise ReviewBindingError("review binding candidate_schema is unsupported")
    candidate_head = _binding_digest(value.get("candidate_head"), "review binding candidate_head")
    candidate_count = _binding_int(
        value.get("candidate_count"), "review binding candidate_count", MAX_CANDIDATES
    )
    carried_count = _binding_int(
        value.get("carried_count"), "review binding carried_count", candidate_count
    )
    for field in _BINDING_FALSE_FIELDS:
        if type(value.get(field)) is not bool or value[field] is not False:
            raise ReviewBindingError(f"review binding {field} must be false")
    head = _binding_digest(value.get("head"), "review binding head")

    safe = {
        "schema": REVIEW_BINDING_SCHEMA,
        "target_sha256": target_digest,
        "generated_at": generated_at,
        "report_schema": "review-report/v1",
        "report_status": "final",
        "report_mode": report_mode,
        "coverage": coverage,
        "timezone": timezone_name,
        "completeness": completeness,
        "authorization": authorization,
        "report_sha256": report_digest,
        "report_bytes": report_bytes,
        "source_pack_schema": SOURCE_PACK_SCHEMA,
        "source_pack_head": source_pack_head,
        "source_count": source_count,
        "total_source_bytes": total_source_bytes,
        "candidate_schema": STATE_SCHEMA_VERSION,
        "candidate_head": candidate_head,
        "candidate_count": candidate_count,
        "carried_count": carried_count,
        **{field: False for field in _BINDING_FALSE_FIELDS},
        "head": head,
    }
    if not hmac.compare_digest(head, _binding_head(safe)):
        raise ReviewBindingError("review binding head does not bind the canonical payload")
    return safe


def validate_review_binding(value: dict) -> None:
    """Reject a malformed, non-private, or non-canonical review binding."""

    _validated_binding(value)


def _read_bound_report(target: str, source: Any) -> tuple[bytes, dict[str, str]]:
    if source.opened_stat.st_size > MAX_REVIEW_BYTES:
        raise InputLimitError("review report exceeds the 2 MiB limit")
    payload = source.handle.read(MAX_REVIEW_BYTES + 1)
    if len(payload) > MAX_REVIEW_BYTES:
        raise InputLimitError("review report exceeded the 2 MiB limit while reading")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReviewBindingError("review report must be valid UTF-8") from exc
    findings = check_text(text)
    if findings:
        summary = "; ".join(findings[:5])
        if len(findings) > 5:
            summary += f"; and {len(findings) - 5} more finding(s)"
        raise ReviewBindingError(f"review report is not mechanically valid: {summary}")
    values, parse_findings = frontmatter(text)
    if parse_findings:
        raise ReviewBindingError("review report frontmatter is not mechanically valid")
    if values.get("status") != "final":
        raise ReviewBindingError("review report status must be final before binding")
    if values.get("target") != target:
        raise ReviewBindingError("review report target does not match the requested target")
    return payload, values


@contextmanager
def _open_review_binding(
    target: str,
    scope_root: str | Path,
    report: str | Path,
    source_pack: dict[str, Any],
    sources: Sequence[str | Path],
    candidate_state: dict[str, Any],
    generated_at: datetime | None = None,
) -> Iterator[dict[str, Any]]:
    try:
        target_digest = target_sha256(target)
        safe_candidates = validate_candidate_state(candidate_state)
    except LedgerError as exc:
        raise ReviewBindingError(f"cannot bind review evidence state: {exc.message}") from exc
    if not hmac.compare_digest(safe_candidates["target_sha256"], target_digest):
        raise ReviewBindingError("candidate state target does not match the requested target")

    with ExitStack() as stack:
        bound_sources = stack.enter_context(_open_source_inputs(scope_root, sources))
        bound_report = stack.enter_context(open_scoped_regular_input(report, scope_root))
        try:
            raw_entries = _read_source_bindings(bound_sources)
            verified_sources = _verify_source_pack_bindings(source_pack, target, raw_entries)
            payload, values = _read_bound_report(target, bound_report)
        except InputLimitError:
            raise
        except LedgerError as exc:
            raise ReviewBindingError(f"cannot bind review evidence state: {exc.message}") from exc
        try:
            report_source_count = int(values["source_count"])
        except (KeyError, ValueError) as exc:
            raise ReviewBindingError("review report source_count must be an integer") from exc
        if report_source_count != verified_sources["source_count"]:
            raise ReviewBindingError("review report source_count does not match the source pack")

        try:
            timestamp = _generated_timestamp(generated_at)
        except SourcePackError as exc:
            raise ReviewBindingError(exc.message) from exc
        binding = {
            "schema": REVIEW_BINDING_SCHEMA,
            "target_sha256": target_digest,
            "generated_at": timestamp,
            "report_schema": values["schema"],
            "report_status": values["status"],
            "report_mode": values["mode"],
            "coverage": values["coverage"],
            "timezone": values["timezone"],
            "completeness": values["completeness"],
            "authorization": values["authorization"],
            "report_sha256": hashlib.sha256(payload).hexdigest(),
            "report_bytes": len(payload),
            "source_pack_schema": verified_sources["schema"],
            "source_pack_head": verified_sources["head"],
            "source_count": verified_sources["source_count"],
            "total_source_bytes": verified_sources["total_bytes"],
            "candidate_schema": safe_candidates["schema_version"],
            "candidate_head": safe_candidates["head"],
            "candidate_count": len(safe_candidates["entries"]),
            "carried_count": sum(
                1 for entry in safe_candidates["entries"] if entry["carried"]
            ),
            **{field: False for field in _BINDING_FALSE_FIELDS},
        }
        binding["head"] = _binding_head(binding)
        yield _validated_binding(binding)


def build_review_binding(
    target: str,
    scope_root: str | Path,
    report: str | Path,
    source_pack: dict[str, Any],
    sources: Sequence[str | Path],
    candidate_state: dict[str, Any],
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Bind one final report while every report/source descriptor remains locked."""

    with _open_review_binding(
        target, scope_root, report, source_pack, sources, candidate_state, generated_at
    ) as binding:
        return binding


def verify_review_binding(
    value: dict[str, Any],
    target: str,
    scope_root: str | Path,
    report: str | Path,
    source_pack: dict[str, Any],
    sources: Sequence[str | Path],
    candidate_state: dict[str, Any],
    require_complete: bool = True,
) -> dict[str, Any]:
    """Rebind every handoff input and write nothing.

    Success proves current identity only.  It never grants implementation or external-action
    authority, even when the bound report records a separate authorization reference.
    """
    if type(require_complete) is not bool:
        raise ReviewBindingVerificationError("require_complete must be boolean")
    expected = _validated_binding(value)
    try:
        generated_at = datetime.fromisoformat(expected["generated_at"].replace("Z", "+00:00"))
        with _open_review_binding(
            target, scope_root, report, source_pack, sources, candidate_state,
            generated_at=generated_at,
        ) as current:
            if not hmac.compare_digest(expected["head"], current["head"]):
                raise ReviewBindingVerificationError(
                    "review binding does not match the current report, sources, candidate state, or target"
                )
            if _binding_stable_payload(expected) != _binding_stable_payload(current):
                raise ReviewBindingVerificationError("review binding stable fields do not match")
            if require_complete and expected["completeness"] != "complete":
                raise IncompleteEvidenceError(
                    "review handoff remains incomplete; verify with require_complete=false only for archival use"
                )
            result = expected
    except (IncompleteEvidenceError, ReviewBindingVerificationError):
        raise
    except LedgerError as exc:
        raise ReviewBindingVerificationError(
            f"review handoff inputs cannot be rebound: {exc.message}"
        ) from exc
    return result
