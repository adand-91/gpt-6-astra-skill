from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from requirement_ledger.cli import main as cli_main
from requirement_ledger.review import build_audit_scaffold
import requirement_ledger.review as review

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_review_report", ROOT / "scripts" / "check_review_report.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestReviewReportContract(unittest.TestCase):
    def call_cli(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli_main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_all_english_templates_pass(self) -> None:
        for name in ("audit-review.md", "daily-review.md", "weekly-review.md"):
            with self.subTest(name=name):
                self.assertEqual([], MODULE.check(ROOT / "templates" / name))

    def test_all_chinese_templates_pass(self) -> None:
        for name in (
            "audit-review.zh-CN.md", "daily-review.zh-CN.md", "weekly-review.zh-CN.md"
        ):
            with self.subTest(name=name):
                self.assertEqual([], MODULE.check(ROOT / "templates" / name))

    def test_missing_timezone_and_offset_fail(self) -> None:
        text = (ROOT / "templates" / "daily-review.md").read_text(encoding="utf-8")
        text = text.replace("timezone: Asia/Shanghai", "timezone: local")
        text = text.replace(
            "coverage: 2026-08-28T08:00:00+08:00 -> 2026-08-29T08:00:00+08:00",
            "coverage: yesterday -> today",
        )
        findings = MODULE.check_text(text)
        self.assertTrue(any("coverage" in finding for finding in findings))
        self.assertTrue(any("timezone" in finding for finding in findings))

    def test_reversed_or_impossible_window_fails(self) -> None:
        text = (ROOT / "templates" / "daily-review.md").read_text(encoding="utf-8")
        text = text.replace(
            "2026-08-28T08:00:00+08:00 -> 2026-08-29T08:00:00+08:00",
            "2026-08-30T08:00:00+08:00 -> 2026-08-29T08:00:00+08:00",
        )
        self.assertTrue(any("earlier" in finding for finding in MODULE.check_text(text)))

        text = text.replace(
            "2026-08-30T08:00:00+08:00 -> 2026-08-29T08:00:00+08:00",
            "2026-99-30T08:00:00+08:00 -> 2026-08-29T08:00:00+08:00",
        )
        self.assertTrue(any("valid offset-aware" in finding for finding in MODULE.check_text(text)))

    def test_timezone_offset_mismatch_fails(self) -> None:
        text = (ROOT / "templates" / "daily-review.md").read_text(encoding="utf-8")
        text = text.replace("timezone: Asia/Shanghai", "timezone: Etc/UTC")
        findings = MODULE.check_text(text)
        self.assertTrue(any("does not match timezone" in finding for finding in findings))

    def test_missing_windows_timezone_database_has_actionable_error(self) -> None:
        missing = review.ZoneInfoNotFoundError("missing timezone database")
        with (
            patch.object(review.sys, "platform", "win32"),
            patch.object(review.importlib.util, "find_spec", return_value=None),
            patch.object(review, "ZoneInfo", side_effect=missing),
        ):
            zone, finding = review._load_timezone("Asia/Shanghai")
        self.assertIsNone(zone)
        self.assertIn("install requirement-ledger with dependencies", finding or "")
        self.assertIn("tzdata", finding or "")

    def test_implementation_authority_requires_reference(self) -> None:
        text = (ROOT / "templates" / "audit-review.md").read_text(encoding="utf-8")
        text = text.replace("authorization: analysis-only", "authorization: implementation-authorized")
        findings = MODULE.check_text(text)
        self.assertTrue(any("concrete authorization_ref" in finding for finding in findings))

    def test_unknown_control_fields_and_invalid_targets_fail_closed(self) -> None:
        original = (ROOT / "templates" / "audit-review.md").read_text(encoding="utf-8")
        for field in (
            "authority_granted: true",
            "execution_authorized: true",
            "source_pack_head: forged",
        ):
            with self.subTest(field=field):
                text = original.replace("status: draft", f"status: draft\n{field}", 1)
                self.assertTrue(any(
                    "unknown frontmatter field" in finding
                    for finding in MODULE.check_text(text)
                ))
        invalid_target = original.replace(
            "target: synthetic-target",
            "target: left\u2028right",
            1,
        )
        self.assertNotEqual([], MODULE.check_text(invalid_target))

    def test_required_sections_cannot_be_deleted(self) -> None:
        cases = (
            ("audit-review.md", "## What must stay"),
            ("audit-review.md", "## One next action"),
            ("daily-review.md", "## Incomplete work"),
            ("weekly-review.md", "## Candidate state and preservation"),
        )
        for template, section in cases:
            with self.subTest(template=template, section=section):
                text = (ROOT / "templates" / template).read_text(encoding="utf-8")
                text = text.replace(section, "## Removed section", 1)
                self.assertTrue(any("missing section" in item for item in MODULE.check_text(text)))

    def test_weekly_cannot_skip_ecosystem_status(self) -> None:
        text = (ROOT / "templates" / "weekly-review.md").read_text(encoding="utf-8")
        text = text.replace("ecosystem_status: not-checked", "ecosystem_status: not-requested")
        self.assertTrue(any(
            "weekly ecosystem_status" in finding for finding in MODULE.check_text(text)
        ))

    def test_checked_ecosystem_requires_a_source_url(self) -> None:
        text = (ROOT / "templates" / "weekly-review.md").read_text(encoding="utf-8")
        text = text.replace("ecosystem_status: not-checked", "ecosystem_status: checked")
        self.assertTrue(any("structured Source block" in finding for finding in MODULE.check_text(text)))

    def test_complete_weekly_source_block_passes(self) -> None:
        text = (ROOT / "templates" / "weekly-review.md").read_text(encoding="utf-8")
        text = text.replace("ecosystem_status: not-checked", "ecosystem_status: checked")
        source = """
### Source source-1

- URL: https://github.com/example/project/releases/tag/v1.2.3
- Owner: example
- Source type: official-release
- Publication/commit date: 2026-08-28
- Retrieval date: 2026-08-29
- Evidence label: SAID
- Verified change or claim: Release v1.2.3 changed the documented interface.
- Relevance: The target uses that interface.
- Licence/access note: Public release notes; no code copied.
- Decision: investigate
"""
        text = text.replace("- Not-checked reason: <record why no source was available>\n", source)
        self.assertEqual([], MODULE.check_text(text))

    def test_weekly_source_missing_fact_label_fails(self) -> None:
        text = (ROOT / "templates" / "weekly-review.md").read_text(encoding="utf-8")
        text = text.replace("ecosystem_status: not-checked", "ecosystem_status: checked")
        source = """
### Source source-1

- URL: https://github.com/example/project
- Owner: example
- Source type: official-repository
- Publication/commit date: 2026-08-28
- Retrieval date: 2026-08-29
- Verified change or claim: A checked claim.
- Relevance: Related interface.
- Licence/access note: MIT.
- Decision: reuse
"""
        text = text.replace("- Not-checked reason: <record why no source was available>\n", source)
        self.assertTrue(any("Evidence label" in finding for finding in MODULE.check_text(text)))

    def test_audit_scaffold_is_valid_analysis_only_and_contains_no_history(self) -> None:
        scaffold = build_audit_scaffold(
            "selected-project", "2026-08-28T08:00:00+08:00",
            "2026-08-29T08:00:00+08:00", "Asia/Shanghai",
        )
        self.assertEqual([], MODULE.check_text(scaffold))
        self.assertIn("authorization: analysis-only", scaffold)
        self.assertIn("authorization_ref: not-applicable", scaffold)
        self.assertIn("source_count: 0", scaffold)
        self.assertIn("does not read historical text or use the network", scaffold)

    def test_review_init_writes_new_0600_scaffold_and_review_check_accepts_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "audit.md"
            command = [
                "review-init", "--mode", "audit", "--target", "selected-skill",
                "--start", "2026-08-28T08:00:00+08:00",
                "--end", "2026-08-29T08:00:00+08:00", "--timezone", "Asia/Shanghai",
                "--output", str(report),
            ]
            code, output, error = self.call_cli(command)
            self.assertEqual(code, 0, error)
            self.assertIn("WROTE_PRIVATE_AUDIT_SCAFFOLD", output)
            if os.name != "nt":
                self.assertEqual(report.stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.call_cli(["review-check", str(report)])[0], 0)
            code, _, error = self.call_cli(command)
            self.assertEqual(code, 4)
            self.assertIn("E_UNSAFE_PATH", error)

    def test_review_init_supports_daily_and_rejects_bad_windows_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "audit.md"
            code, _, error = self.call_cli([
                "review-init", "--target", "selected-skill", "--start", "2026-08-29T08:00:00+08:00",
                "--end", "2026-08-28T08:00:00+08:00", "--timezone", "Asia/Shanghai",
                "--output", str(report),
            ])
            self.assertEqual(code, 2)
            self.assertIn("E_REVIEW_INPUT: start must be earlier", error)
            self.assertNotIn("Traceback", error)

            daily = Path(tmp) / "daily.md"
            code, output, error = self.call_cli([
                "review-init", "--mode", "daily", "--target", "selected-skill",
                "--at", "2026-08-29T08:00:00+08:00", "--timezone", "Asia/Shanghai",
                "--output", str(daily),
            ])
            self.assertEqual(code, 0, error)
            self.assertIn("WROTE_PRIVATE_DAILY_SCAFFOLD", output)
            self.assertEqual(self.call_cli(["review-check", str(daily)])[0], 0)

            bad = Path(tmp) / "bad.md"
            code, _, error = self.call_cli([
                "review-init", "--mode", "weekly", "--target", "selected-skill",
                "--at", "2026-08-29T08:00:00+08:00", "--start", "2026-08-20T08:00:00+08:00",
                "--end", "2026-08-27T08:00:00+08:00", "--timezone", "Asia/Shanghai",
                "--output", str(bad),
            ])
            self.assertEqual(code, 2)
            self.assertIn("E_REVIEW_INPUT: at cannot be combined", error)
            self.assertNotIn("Traceback", error)

    def test_review_check_rejects_symlink_and_oversized_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "real.md"
            real.write_text("---\n", encoding="utf-8")
            link = root / "link.md"
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                pass
            else:
                code, _, error = self.call_cli(["review-check", str(link)])
                self.assertEqual(code, 4)
                self.assertIn("E_UNSAFE_PATH", error)

            large = root / "large.md"
            large.write_text("x" * 32, encoding="utf-8")
            with patch.object(review, "MAX_REVIEW_BYTES", 16):
                code, _, error = self.call_cli(["review-check", str(large)])
            self.assertEqual(code, 6)
            self.assertIn("E_SCHEMA: review report exceeds", error)


if __name__ == "__main__":
    unittest.main()
