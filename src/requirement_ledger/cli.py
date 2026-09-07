"""Console interface.  It never runs project code or writes a real project worktree."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .errors import LedgerError
from .git_evidence import bind_repo
from .pipeline import (analyze_evidence, build_codex_scan_bundle, build_evidence_bundle, build_fix_proposals,
                       render_markdown_report, share_report, synthetic_demo_bundle,
                       validate_outcomes)
from .privacy import finding_counts
from .review import ReviewInputError, check as check_review_report
from .review import write_review_scaffold
from .safeio import (explicit_regular_file, new_output_directory, private_output_path,
                     read_json_file, share_output_path, write_new_json, write_new_text)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="requirement-ledger",
        description="Offline evidence and repair-planning pipeline for an explicit Git project.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="check an explicit repository without changing it")
    doctor.add_argument("--repo", required=True)
    doctor.add_argument("--json", action="store_true")

    scan = sub.add_parser("scan", help="create a private evidence bundle from explicit inputs")
    scan.add_argument("--repo", required=True)
    scan.add_argument("--input", action="append", required=True, dest="inputs")
    scan.add_argument("--provider", choices=("auto", "claude", "codex", "text"), default="auto")
    scan.add_argument("--test-log", action="append", default=[])
    scan.add_argument("--since")
    scan.add_argument("--until")
    scan.add_argument("--output", required=True, help="new path ending in .private.json")

    codex_scan = sub.add_parser(
        "codex-scan",
        help="bind and scan one explicit Codex export inside an approved scope",
    )
    codex_scan.add_argument("--repo", required=True)
    codex_scan.add_argument("--input", required=True)
    codex_scan.add_argument("--scope-root", required=True)
    codex_scan.add_argument("--target", required=True, help="single-line non-path target reference")
    codex_scan.add_argument("--task-ref", required=True, help="single-line non-path Codex task reference")
    codex_scan.add_argument("--since", required=True)
    codex_scan.add_argument("--until", required=True)
    codex_scan.add_argument("--timezone", required=True, help="explicit IANA timezone")
    codex_scan.add_argument(
        "--exclude",
        action="append",
        default=[],
        choices=("automation", "delegation", "subagent", "system", "unrelated", "not-provided"),
        help="declare a fixed class that was not selected; repeat as needed",
    )
    codex_scan.add_argument("--output", required=True, help="new path ending in .private.json")

    analyze = sub.add_parser("analyze", help="conservatively classify a private evidence bundle")
    analyze.add_argument("--evidence", required=True)
    analyze.add_argument("--output", required=True)

    report = sub.add_parser("report", help="build a quote-free share-facing report")
    report.add_argument("--analysis", required=True)
    report.add_argument("--output", required=True)

    suggest = sub.add_parser("suggest", help="build local DRAFT — NOT SENT repair plans")
    suggest.add_argument("--analysis", required=True)
    suggest.add_argument("--output", required=True)

    verify = sub.add_parser("verify", help="compare externally produced baseline/after outcomes")
    verify.add_argument("--oracle", required=True)
    verify.add_argument("--oracle-digest", required=True,
                        help="64-hex digest binding argv/cwd/env/fixtures for the frozen oracle")
    verify.add_argument("--baseline", required=True)
    verify.add_argument("--after", required=True)
    verify.add_argument("--output", required=True)

    privacy = sub.add_parser("privacy-check", help="scan a file; values are never printed")
    privacy.add_argument("path")

    review_init = sub.add_parser(
        "review-init",
        help="create a new private, analysis-only audit/daily/weekly review scaffold",
    )
    review_init.add_argument("--mode", choices=("audit", "daily", "weekly"), default="audit")
    review_init.add_argument("--target", required=True,
                             help="explicit conversation, Skill, or project target")
    review_init.add_argument("--start", help="explicit offset-aware ISO-8601 window start")
    review_init.add_argument("--end", help="explicit offset-aware ISO-8601 window end")
    review_init.add_argument("--timezone", required=True, help="explicit IANA timezone")
    review_init.add_argument(
        "--at",
        help="offset-aware reference timestamp for the most recently completed daily/weekly window",
    )
    review_init.add_argument(
        "--boundary-hour", type=int, default=8,
        help="local daily/weekly boundary hour from 0 through 23 (default: 8)",
    )
    review_init.add_argument("--output", required=True, help="new private Markdown output path")

    review_check = sub.add_parser("review-check", help="mechanically validate one explicit review report")
    review_check.add_argument("report", help="explicit Markdown report path")

    demo = sub.add_parser("demo", help="write a complete synthetic, offline v0.1 walkthrough")
    demo.add_argument("--output-dir", required=True)
    return parser


def _print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _load_outcome(path: str) -> dict[str, Any]:
    source = explicit_regular_file(path)
    if source.stat().st_size > 1024 * 1024:
        raise ValueError("outcome JSON exceeds the 1 MiB limit")
    raw = source.read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("outcome must be a JSON object")
    return value


def run(args: argparse.Namespace) -> int:
    if args.command == "doctor":
        _, snapshot = bind_repo(args.repo)
        result = {
            "status": "READY_READONLY",
            "repository": snapshot,
            "network_used": False,
            "can_run_project_code": False,
            "can_write_real_worktree": False,
        }
        _print(result) if args.json else print(
            f"READY_READONLY head={snapshot['head'][:12]} dirty={snapshot['dirty_entries']} "
            "network=no project-execution=no real-worktree-write=no"
        )
        return 0

    if args.command == "scan":
        out = private_output_path(args.output)
        bundle = build_evidence_bundle(args.repo, args.inputs, args.provider, args.test_log,
                                       args.since, args.until)
        write_new_json(out, bundle, private=True)
        print(f"WROTE_PRIVATE_EVIDENCE {out}")
        return 0

    if args.command == "codex-scan":
        out = private_output_path(args.output)
        bundle = build_codex_scan_bundle(
            args.repo,
            args.input,
            scope_root=args.scope_root,
            target=args.target,
            task_ref=args.task_ref,
            since=args.since,
            until=args.until,
            timezone_name=args.timezone,
            declared_exclusions=args.exclude,
        )
        write_new_json(out, bundle, private=True)
        print(f"WROTE_PRIVATE_CODEX_EVIDENCE {out}")
        return 0

    if args.command == "analyze":
        private = read_json_file(args.evidence, "private-evidence")
        out = share_output_path(args.output, (".json",))
        value = analyze_evidence(private)
        write_new_json(out, value, private=True)
        print(f"WROTE_LOCAL_ANALYSIS {out}")
        return 0

    if args.command == "report":
        analysis = read_json_file(args.analysis, "analysis")
        value = share_report(analysis)
        out = share_output_path(args.output)
        if out.suffix == ".md":
            write_new_text(out, render_markdown_report(value), private=False)
        else:
            write_new_json(out, value, private=False)
        print(f"WROTE_REVIEW_REQUIRED_REPORT {out}")
        return 0

    if args.command == "suggest":
        analysis = read_json_file(args.analysis, "analysis")
        out = share_output_path(args.output, (".json",))
        value = build_fix_proposals(analysis)
        write_new_json(out, value, private=True)
        print(f"WROTE_DRAFT_NOT_SENT {out}")
        return 0

    if args.command == "verify":
        out = share_output_path(args.output, (".json",))
        value = validate_outcomes(args.oracle, args.oracle_digest,
                                  _load_outcome(args.baseline), _load_outcome(args.after))
        write_new_json(out, value, private=True)
        print(f"WROTE_VALIDATION {out}")
        return 0

    if args.command == "privacy-check":
        source = explicit_regular_file(args.path)
        if source.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("privacy-check input exceeds the 10 MiB limit")
        text = source.read_text(encoding="utf-8", errors="replace")
        findings = finding_counts(text)
        _print({"status": "BLOCK" if findings else "AUTOMATED_CHECK_PASSED_REVIEW_REQUIRED",
                "findings": findings, "matched_values_printed": False})
        return 3 if findings else 0

    if args.command == "review-init":
        if args.at and (args.start is not None or args.end is not None):
            raise ReviewInputError("at cannot be combined with an explicit start/end window")
        reference = None
        if args.at:
            value = args.at[:-1] + "+00:00" if args.at.endswith("Z") else args.at
            try:
                reference = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ReviewInputError("at must be an offset-aware ISO-8601 timestamp") from exc
            if reference.tzinfo is None or reference.utcoffset() is None:
                raise ReviewInputError("at must be an offset-aware ISO-8601 timestamp")
        output = write_review_scaffold(
            args.output,
            args.mode,
            args.target,
            args.timezone,
            start=args.start,
            end=args.end,
            boundary_hour=args.boundary_hour,
            now=reference,
        )
        print(f"WROTE_PRIVATE_{args.mode.upper()}_SCAFFOLD {output}")
        return 0

    if args.command == "review-check":
        findings = check_review_report(Path(args.report))
        if findings:
            print("REVIEW_REPORT_INVALID")
            for finding in findings:
                print(f"  - {finding}")
            return 1
        print("REVIEW_REPORT_VALID")
        return 0

    if args.command == "demo":
        root = new_output_directory(args.output_dir)
        bundle = synthetic_demo_bundle()
        analysis = analyze_evidence(bundle)
        proposals = build_fix_proposals(analysis)
        report = share_report(analysis)
        oracle_digest = hashlib.sha256(b"synthetic-regression:v1").hexdigest()
        validation = validate_outcomes(
            "synthetic-regression", oracle_digest,
            {"oracle": "synthetic-regression", "oracle_digest": oracle_digest, "exit_code": 1},
            {"oracle": "synthetic-regression", "oracle_digest": oracle_digest, "exit_code": 0},
        )
        fixed_time = "2026-01-01T00:00:00+00:00"
        analysis["created_at"] = fixed_time
        proposals["created_at"] = fixed_time
        report["created_at"] = fixed_time
        write_new_json(root / "01-evidence.private.json", bundle, private=True)
        write_new_json(root / "02-analysis.json", analysis, private=True)
        write_new_json(root / "03-proposals.json", proposals, private=True)
        write_new_text(root / "04-report.md", render_markdown_report(report), private=False)
        write_new_json(root / "05-validation.json", validation, private=True)
        print(f"DEMO_COMPLETE {root}")
        return 0
    raise AssertionError("unreachable")


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
        return run(args)
    except LedgerError as exc:
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        return exc.exit_code
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"E_INPUT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
