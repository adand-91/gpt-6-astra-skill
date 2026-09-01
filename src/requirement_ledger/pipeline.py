"""Deterministic evidence, analysis, proposal, report, and verification pipeline."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import stat
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .codex_input import build_codex_input_envelope, validate_codex_request
from .git_evidence import bind_repo
from .models import (EvidenceItem, FixProposal, IssueRecord, SourceRef, ValidationResult,
                     dataclass_dict, envelope)
from .privacy import assert_automated_privacy_check, manifest_for_private_texts
from .safeio import explicit_regular_file
from .review import validate_window
from .transcript import parse_explicit_transcript, parse_scoped_codex_transcript

MAX_EXPLICIT_INPUTS = 20
MAX_TEST_LOG_BYTES = 10 * 1024 * 1024


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _opaque(key: bytes, namespace: str, value: str) -> str:
    digest = hmac.new(key, f"{namespace}\0{value}".encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{namespace}_{digest[:16]}"


def _source_completeness(items: list[dict[str, Any]]) -> str:
    return "incomplete" if any(item.get("completeness") != "complete" for item in items) else "complete"


def _test_log_content_signature(info: os.stat_result) -> tuple[int, int]:
    """Return content metadata stable across path and handle stats.

    Same-file identity is checked separately with ``os.path.samestat``.  On
    Windows, ``lstat`` and ``fstat`` can report different non-content fields
    for the same file, so a combined identity/content tuple causes false
    ``E_INPUT_CHANGED`` results.
    """
    return (info.st_size, info.st_mtime_ns)


def _read_test_log_stable(path: Path) -> tuple[str, int, list[dict[str, Any]], str]:
    """Hash and parse exactly the same bytes from one stable file descriptor."""
    from .errors import InputChangedError, UnsafePathError

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor: int | None = None
    try:
        path_before = os.lstat(path)
        descriptor = os.open(path, flags)
        opened = os.fstat(descriptor)
        initial_signature = _test_log_content_signature(opened)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink > 1:
            raise UnsafePathError("test log must remain a single-linked regular file")
        if not os.path.samestat(path_before, opened):
            raise InputChangedError("test log changed before it could be bound")
        if opened.st_size > MAX_TEST_LOG_BYTES:
            raise UnsafePathError("test log exceeds the v0.1 10 MiB per-file limit")

        payload = bytearray()
        digest_builder = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            payload.extend(chunk)
            digest_builder.update(chunk)
            if len(payload) > MAX_TEST_LOG_BYTES:
                raise UnsafePathError("test log exceeded the v0.1 10 MiB limit while reading")

        final_fd = os.fstat(descriptor)
        path_after = os.lstat(path)
        if (not stat.S_ISREG(path_after.st_mode) or path_after.st_nlink > 1
                or not os.path.samestat(opened, path_after)
                or initial_signature != _test_log_content_signature(final_fd)
                or initial_signature != _test_log_content_signature(path_after)):
            raise InputChangedError("test log changed while it was being read")
    except (InputChangedError, UnsafePathError):
        raise
    except OSError as exc:
        raise UnsafePathError(f"cannot read the explicit test log: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)

    completeness = "complete"
    try:
        text = bytes(payload).decode("utf-8")
    except UnicodeDecodeError:
        text = bytes(payload).decode("utf-8", errors="replace")
        completeness = "incomplete"
    hits: list[dict[str, Any]] = []
    for line in text.splitlines():
        low = line.lower()
        if "failed" not in low and "error" not in low and "traceback" not in low:
            continue
        if len(hits) >= 100:
            completeness = "incomplete"
            continue
        if len(line) > 8000:
            completeness = "incomplete"
        hits.append({"kind": "test_failure", "private_text": line[:8000],
                     "occurred_at": None, "metadata": {"project_reference": True}})
    return digest_builder.hexdigest(), len(payload), hits, completeness


_PUBLIC_TITLES = {
    "Correction candidate requires project review",
    "Tool failure requires reproduction",
    "Supplied test failure requires isolation",
    "Evidence item requires review",
}
_PUBLIC_RATIONALES = {
    "A correction is evidence of divergence, but does not identify the faulty layer.",
    "A tool error alone cannot distinguish project, environment, or upstream causes.",
    "The log points toward project-local behaviour, but no clean comparison was supplied.",
    "The evidence is insufficient for a confirmed scope.",
}


def build_evidence_bundle(
    repo: str | Path,
    inputs: list[str | Path],
    provider: str = "auto",
    test_logs: list[str | Path] | None = None,
    since: str | None = None,
    until: str | None = None,
    deterministic_key: bytes | None = None,
    *,
    _parsed_inputs: list[dict[str, Any]] | None = None,
    _codex_input_envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not inputs:
        from .errors import UnsafePathError
        raise UnsafePathError("at least one explicit transcript input is required")
    if len(inputs) > MAX_EXPLICIT_INPUTS or len(test_logs or []) > MAX_EXPLICIT_INPUTS:
        from .errors import UnsafePathError
        raise UnsafePathError("v0.1 accepts at most 20 transcript inputs and 20 test logs per run")
    root, git_snapshot = bind_repo(repo)
    key = deterministic_key or secrets.token_bytes(32)
    run_id = _opaque(key, "run", git_snapshot["head"] + _now())
    sources: list[SourceRef] = []
    evidence: list[EvidenceItem] = []
    private_texts: list[str] = []

    repo_source_id = _opaque(key, "src", git_snapshot["head"] + git_snapshot["status_digest"])
    sources.append(SourceRef(
        id=repo_source_id,
        kind="git",
        digest=git_snapshot["status_digest"],
        bytes=0,
        parser="fixed-read-only-git",
    ))

    if _parsed_inputs is not None and len(_parsed_inputs) != len(inputs):
        from .errors import SchemaError
        raise SchemaError("preparsed input count does not match the explicit input count")
    parsed_inputs = _parsed_inputs or [
        parse_explicit_transcript(raw, provider=provider, since=since, until=until)
        for raw in inputs
    ]
    for parsed in parsed_inputs:
        source_id = _opaque(key, "src", parsed["digest"])
        sources.append(SourceRef(
            id=source_id,
            kind="transcript",
            digest=parsed["digest"],
            bytes=parsed["bytes"],
            completeness=parsed["completeness"],
            parser=parsed["provider"],
        ))
        for index, event in enumerate(parsed["events"]):
            text = event.get("private_text") or ""
            if text:
                private_texts.append(text)
            evidence.append(EvidenceItem(
                id=_opaque(key, "ev", f"{parsed['digest']}:{index}:{event['kind']}"),
                kind=event["kind"],
                source_ref=source_id,
                label=("SAID" if event["kind"] in (
                    "user_message", "correction", "assistant_message", "tool_call"
                ) else "INFERRED"),
                summary={
                    "user_message": "A user message was recorded.",
                    "correction": "A correction candidate was recorded; semantic review is required.",
                    "assistant_message": "An assistant message was recorded.",
                    "tool_call": "A tool call was recorded.",
                    "tool_error": "A tool output matched conservative error markers.",
                }.get(event["kind"], "An event was recorded."),
                occurred_at=event.get("occurred_at"),
                completeness=parsed["completeness"],
                private_text=text or None,
                metadata=event.get("metadata") or {},
            ))

    for raw in test_logs or []:
        path = explicit_regular_file(raw)
        digest, byte_count, log_evidence, completeness = _read_test_log_stable(path)
        source_id = _opaque(key, "src", digest)
        sources.append(SourceRef(id=source_id, kind="test-log", digest=digest,
                                 bytes=byte_count, completeness=completeness,
                                 parser="text-test-log"))
        for index, item in enumerate(log_evidence):
            text = item["private_text"]
            private_texts.append(text)
            evidence.append(EvidenceItem(
                id=_opaque(key, "ev", f"{digest}:{index}:test_failure"),
                kind="test_failure",
                source_ref=source_id,
                label="INFERRED",
                summary="A supplied test log line matched conservative failure markers.",
                completeness=completeness,
                private_text=text,
                metadata=item["metadata"],
            ))

    evidence.append(EvidenceItem(
        id=_opaque(key, "ev", "git-snapshot" + git_snapshot["status_digest"]),
        kind="git_snapshot",
        source_ref=repo_source_id,
        label="SAID",
        summary="A read-only Git snapshot was captured without reading remotes.",
        metadata=git_snapshot,
    ))
    source_dicts = [dataclass_dict(item) for item in sources]
    payload = {
        "run_id": run_id,
        "created_at": _now(),
        "privacy": "private-local-evidence",
        "repository": git_snapshot,
        "sources": source_dicts,
        "evidence": [dataclass_dict(item) for item in evidence],
        "completeness": _source_completeness(source_dicts),
        "privacy_manifest": manifest_for_private_texts(private_texts),
        "network_used": False,
        "commands_executed": ["read-only git probes"],
        "repo_path_stored": False,
        "private_note": "May contain raw user text. Do not share this file.",
    }
    if _codex_input_envelope is not None:
        payload["codex_input_envelope"] = _codex_input_envelope
    return envelope("private-evidence", payload)


def build_codex_scan_bundle(
    repo: str | Path,
    source: str | Path,
    *,
    scope_root: str | Path,
    target: str,
    task_ref: str,
    since: str,
    until: str,
    timezone_name: str,
    declared_exclusions: list[str] | None = None,
    deterministic_key: bytes | None = None,
) -> dict[str, Any]:
    """Build private evidence plus a non-textual envelope for one bounded Codex export."""

    target, task_ref, exclusions = validate_codex_request(
        target, task_ref, declared_exclusions
    )
    start_at, end_at, _ = validate_window(since, until, timezone_name)
    parsed = parse_scoped_codex_transcript(
        source, scope_root, since=start_at, until=end_at
    )
    input_envelope = build_codex_input_envelope(
        parsed,
        target=target,
        task_ref=task_ref,
        start=start_at,
        end=end_at,
        timezone_name=timezone_name,
        declared_exclusions=exclusions,
    )
    return build_evidence_bundle(
        repo,
        [source],
        provider="codex",
        test_logs=[],
        since=since,
        until=until,
        deterministic_key=deterministic_key,
        _parsed_inputs=[parsed],
        _codex_input_envelope=input_envelope,
    )


def _issue_for(item: dict[str, Any], completeness: str, index: int) -> IssueRecord:
    kind = item.get("kind")
    suspected = "project-local" if kind == "test_failure" else "unknown"
    title = {
        "correction": "Correction candidate requires project review",
        "tool_error": "Tool failure requires reproduction",
        "test_failure": "Supplied test failure requires isolation",
    }.get(kind, "Evidence item requires review")
    rationale = {
        "correction": "A correction is evidence of divergence, but does not identify the faulty layer.",
        "tool_error": "A tool error alone cannot distinguish project, environment, or upstream causes.",
        "test_failure": "The log points toward project-local behaviour, but no clean comparison was supplied.",
    }.get(kind, "The evidence is insufficient for a confirmed scope.")
    return IssueRecord(
        id=f"issue_{index:04d}",
        title=title,
        label="INFERRED",
        suspected_scope=suspected,
        scope="unknown",
        decision_status="blocked" if completeness != "complete" else "candidate",
        evidence_refs=[str(item.get("id"))],
        exclusions_checked=[],
        rationale=rationale,
        completeness=completeness if completeness in ("complete", "incomplete", "unstable") else "incomplete",
    )


def analyze_evidence(bundle: dict[str, Any]) -> dict[str, Any]:
    issues: list[IssueRecord] = []
    overall = str(bundle.get("completeness") or "incomplete")
    for item in bundle.get("evidence", []):
        if not isinstance(item, dict) or item.get("kind") not in ("correction", "tool_error", "test_failure"):
            continue
        completeness = "incomplete" if overall != "complete" else str(item.get("completeness") or "complete")
        issues.append(_issue_for(item, completeness, len(issues) + 1))
    return envelope("analysis", {
        "run_id": bundle.get("run_id"),
        "created_at": _now(),
        "issues": [dataclass_dict(issue) for issue in issues],
        "counts": dict(Counter(item.get("kind", "unknown") for item in bundle.get("evidence", []) if isinstance(item, dict))),
        "classification_contract": {
            "default_scope": "unknown",
            "upstream_requires": "independent projects plus a clean minimal reproduction and exclusions",
            "personal_requires": "explicitly authorised personal-config comparison",
            "project_local_requires": "direct repository evidence plus a clean comparison",
        },
        "private_evidence_required_for_details": True,
        "network_used": False,
    })


def build_fix_proposals(analysis: dict[str, Any]) -> dict[str, Any]:
    proposals: list[FixProposal] = []
    for index, issue in enumerate(analysis.get("issues", []), 1):
        issue_id = str(issue.get("id"))
        proposals.append(FixProposal(
            id=f"proposal_{index:04d}",
            issue_id=issue_id,
            title="DRAFT — NOT SENT — isolate, reproduce, and patch",
            summary="Use the referenced private evidence locally; create the smallest regression-backed patch.",
            apply_status="not-applied",
            permitted_targets=["ordinary text source files in an isolated copy", "new regression tests"],
            prohibited_actions=[
                "real worktree writes without a new object-bound approval",
                "dependency installation or network access",
                "commit, push, Issue, PR, Release, telemetry, or upload",
                "delete, rename, chmod, binary, submodule, or secret-file changes",
            ],
            verification_plan=[
                "Freeze one explicit oracle before preparing a patch.",
                "Record the baseline with the same oracle in an isolated environment.",
                "Apply only the exact reviewed patch in the isolated copy.",
                "Run the same oracle; improved means baseline failed and after passed.",
                "Review unrelated regressions and inspect the diff before any real apply decision.",
            ],
            rollback_plan=["Discard the isolated copy; the real worktree must remain unchanged."],
        ))
    return envelope("fix-proposals", {
        "run_id": analysis.get("run_id"),
        "created_at": _now(),
        "status": "DRAFT — NOT SENT",
        "proposals": [dataclass_dict(item) for item in proposals],
        "external_actions": [],
    })


def share_report(analysis: dict[str, Any]) -> dict[str, Any]:
    safe_issues: list[dict[str, Any]] = []
    allowed_scopes = {"upstream", "project-local", "personal", "unknown"}
    allowed_decisions = {"candidate", "confirmed", "blocked"}
    allowed_labels = {"SAID", "INFERRED", "UNKNOWN"}
    allowed_completeness = {"complete", "incomplete", "unstable"}
    allowed_counts = {
        "user_message", "correction", "assistant_message", "tool_call", "tool_error",
        "test_failure", "git_snapshot",
    }
    for index, issue in enumerate(analysis.get("issues", []), 1):
        if not isinstance(issue, dict):
            continue
        title = issue.get("title")
        rationale = issue.get("rationale")
        safe_issues.append({
            "id": f"issue_{index:04d}",
            "title": title if title in _PUBLIC_TITLES else "Evidence item requires review",
            "label": issue.get("label") if issue.get("label") in allowed_labels else "UNKNOWN",
            "suspected_scope": (issue.get("suspected_scope")
                                if issue.get("suspected_scope") in allowed_scopes else "unknown"),
            "scope": issue.get("scope") if issue.get("scope") in allowed_scopes else "unknown",
            "decision_status": (issue.get("decision_status")
                                if issue.get("decision_status") in allowed_decisions else "blocked"),
            "rationale": (rationale if rationale in _PUBLIC_RATIONALES
                          else "The evidence is insufficient for a confirmed scope."),
            "completeness": (issue.get("completeness")
                             if issue.get("completeness") in allowed_completeness else "incomplete"),
        })
    raw_counts = analysis.get("counts") if isinstance(analysis.get("counts"), dict) else {}
    safe_counts = {
        key: value for key, value in raw_counts.items()
        if key in allowed_counts and isinstance(value, int) and value >= 0
    }
    report = envelope("share-report", {
        "run_id": "withheld",
        "created_at": _now(),
        "summary": {
            "issue_candidates": len(safe_issues),
            "counts": safe_counts,
            "confirmed_upstream": 0,
            "confirmed_project_local": 0,
            "confirmed_personal": 0,
            "unknown_or_candidate": len(safe_issues),
        },
        "issues": safe_issues,
        "privacy_statement": (
            "Automated privacy checks passed for this generated file. This is not proof that "
            "the file is safe to share; a human must review it."
        ),
        "raw_quotes_included": False,
        "paths_included": False,
        "network_used": False,
    })
    assert_automated_privacy_check(report)
    return report


def render_markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Requirement Ledger v0.1 Report",
        "",
        "> Automated privacy checks passed for this generated file. This is not proof that",
        "> the file is safe to share; a human must review it.",
        "",
        "## Summary",
        "",
        f"- Issue candidates: {summary['issue_candidates']}",
        f"- Confirmed upstream: {summary['confirmed_upstream']}",
        f"- Confirmed project-local: {summary['confirmed_project_local']}",
        f"- Confirmed personal: {summary['confirmed_personal']}",
        f"- Unknown or candidate: {summary['unknown_or_candidate']}",
        "- Raw quotes: not included",
        "- Local paths: not included",
        "- Network used: no",
        "",
        "## Issue candidates",
        "",
    ]
    if not report["issues"]:
        lines.append("No correction, tool-error, or test-failure candidates were found in the explicit inputs.")
    for issue in report["issues"]:
        lines += [
            f"### {issue['id']} — {issue['title']}",
            "",
            f"- Evidence label: `{issue['label']}`",
            f"- Suspected scope: `{issue['suspected_scope']}`",
            f"- Confirmed scope: `{issue['scope']}`",
            f"- Decision: `{issue['decision_status']}`",
            f"- Completeness: `{issue['completeness']}`",
            f"- Rationale: {issue['rationale']}",
            "",
        ]
    text = "\n".join(lines).rstrip() + "\n"
    assert_automated_privacy_check(text)
    return text


def _valid_exit_code(value: Any) -> bool:
    return type(value) is int and 0 <= value <= 255


def _valid_oracle_digest(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def validate_outcomes(oracle: str, oracle_digest: str, baseline: dict[str, Any],
                      after: dict[str, Any]) -> dict[str, Any]:
    digest_valid = _valid_oracle_digest(oracle_digest)
    same = (baseline.get("oracle") == oracle == after.get("oracle")
            and baseline.get("oracle_digest") == oracle_digest == after.get("oracle_digest")
            and digest_valid)
    before_code, after_code = baseline.get("exit_code"), after.get("exit_code")
    if not same or not _valid_exit_code(before_code) or not _valid_exit_code(after_code):
        status, rationale = "inconclusive", "Oracle name/digest or bounded integer exit codes do not match."
    elif before_code != 0 and after_code == 0:
        status, rationale = "improved", "The digest-bound oracle failed at baseline and passed after the intervention."
    elif before_code == 0 and after_code != 0:
        status, rationale = "regressed", "The digest-bound oracle passed at baseline and failed after the intervention."
    elif before_code == after_code:
        status, rationale = "unchanged", "The digest-bound oracle exit outcome did not change."
    else:
        status, rationale = "inconclusive", "Both runs failed with different exit outcomes."
    result = ValidationResult(
        oracle=oracle,
        oracle_digest=oracle_digest if digest_valid else None,
        baseline_exit_code=before_code if _valid_exit_code(before_code) else None,
        after_exit_code=after_code if _valid_exit_code(after_code) else None,
        status=status,
        rationale=rationale,
        same_oracle=same,
    )
    return envelope("validation", {"result": dataclass_dict(result), "commands_run_by_tool": []})


def synthetic_demo_bundle() -> dict[str, Any]:
    key = b"requirement-ledger-v0.1-synthetic-demo"
    source = SourceRef(id="src_demo", kind="transcript", digest=hashlib.sha256(b"demo").hexdigest(),
                       bytes=128, parser="synthetic")
    items = [
        EvidenceItem(id="ev_demo_correction", kind="correction", source_ref=source.id,
                     label="SAID", summary="A synthetic correction candidate was recorded.",
                     private_text="This is synthetic: keep the existing API and fix the retry loop."),
        EvidenceItem(id="ev_demo_error", kind="tool_error", source_ref=source.id,
                     label="INFERRED", summary="A synthetic tool failure was recorded.",
                     private_text="SyntheticError: retry limit reached", metadata={"tool": "synthetic-test"}),
        EvidenceItem(id="ev_demo_git", kind="git_snapshot", source_ref="repository", label="SAID",
                     summary="A synthetic clean Git snapshot was recorded.", metadata={"dirty_entries": 0}),
    ]
    return envelope("private-evidence", {
        "run_id": _opaque(key, "run", "demo"),
        "created_at": "2026-01-01T00:00:00+00:00",
        "privacy": "private-local-evidence",
        "repository": {"head": "0" * 40, "dirty_entries": 0, "read_only": True},
        "sources": [dataclass_dict(source)],
        "evidence": [dataclass_dict(item) for item in items],
        "completeness": "complete",
        "privacy_manifest": manifest_for_private_texts([item.private_text or "" for item in items]),
        "network_used": False,
        "repo_path_stored": False,
        "private_note": "Synthetic data only.",
    })
