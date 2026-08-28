"""Versioned data model shared by every v0.1 command.

The model intentionally separates facts, interpretation, proposals, and validation.  A
proposal can never be mistaken for an applied patch because the state is explicit in data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from . import __version__

SCHEMA_VERSION = "1.0"
TOOL_VERSION = __version__

Completeness = Literal["complete", "incomplete", "unstable"]
EvidenceLabel = Literal["SAID", "INFERRED", "UNKNOWN"]
Scope = Literal["upstream", "project-local", "personal", "unknown"]
DecisionStatus = Literal["candidate", "confirmed", "blocked"]
ApplyStatus = Literal["not-applied", "isolation-only"]
ValidationStatus = Literal["improved", "unchanged", "regressed", "inconclusive"]


@dataclass(frozen=True)
class SourceRef:
    id: str
    kind: str
    digest: str
    bytes: int
    completeness: Completeness = "complete"
    parser: str = "unknown"
    parser_version: str = "1"


@dataclass(frozen=True)
class EvidenceItem:
    id: str
    kind: str
    source_ref: str
    label: EvidenceLabel
    summary: str
    occurred_at: str | None = None
    completeness: Completeness = "complete"
    private_text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IssueRecord:
    id: str
    title: str
    label: EvidenceLabel
    suspected_scope: Scope
    scope: Scope
    decision_status: DecisionStatus
    evidence_refs: list[str]
    exclusions_checked: list[str]
    rationale: str
    completeness: Completeness


@dataclass(frozen=True)
class FixProposal:
    id: str
    issue_id: str
    title: str
    summary: str
    apply_status: ApplyStatus
    permitted_targets: list[str]
    prohibited_actions: list[str]
    verification_plan: list[str]
    rollback_plan: list[str]


@dataclass(frozen=True)
class ValidationResult:
    oracle: str
    oracle_digest: str | None
    baseline_exit_code: int | None
    after_exit_code: int | None
    status: ValidationStatus
    rationale: str
    same_oracle: bool


def dataclass_dict(value: Any) -> dict[str, Any]:
    return asdict(value)


def envelope(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "kind": kind,
        **payload,
    }
