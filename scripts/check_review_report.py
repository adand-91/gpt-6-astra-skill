#!/usr/bin/env python3
"""Backward-compatible thin wrapper for the packaged report checker."""

from __future__ import annotations

import sys
from pathlib import Path

if not __package__:  # Support ``python scripts/check_review_report.py`` from a checkout.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from requirement_ledger.errors import LedgerError  # noqa: E402
from requirement_ledger.review import check, check_text, frontmatter  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate a Requirement Ledger review report.")
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    try:
        findings = check(args.report)
    except LedgerError as exc:
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        return exc.exit_code
    if findings:
        print("REVIEW_REPORT_INVALID")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("REVIEW_REPORT_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
