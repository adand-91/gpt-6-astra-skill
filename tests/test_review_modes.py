from __future__ import annotations

from datetime import datetime
from pathlib import Path
import unittest

from requirement_ledger.review import (
    ReviewInputError,
    build_daily_scaffold,
    build_review_scaffold,
    build_weekly_scaffold,
    calculate_review_window,
    check_text,
)


class TestReviewModes(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_daily_uses_last_completed_boundary_and_includes_exact_boundary(self) -> None:
        before = datetime.fromisoformat("2026-09-01T07:59:00+08:00")
        start, end = calculate_review_window("daily", "Asia/Shanghai", now=before)
        self.assertEqual(start.isoformat(), "2026-08-30T08:00:00+08:00")
        self.assertEqual(end.isoformat(), "2026-08-31T08:00:00+08:00")

        exact = datetime.fromisoformat("2026-09-01T08:00:00+08:00")
        start, end = calculate_review_window("daily", "Asia/Shanghai", now=exact)
        self.assertEqual(start.isoformat(), "2026-08-31T08:00:00+08:00")
        self.assertEqual(end.isoformat(), "2026-09-01T08:00:00+08:00")

        midnight = datetime.fromisoformat("2026-09-01T00:00:00+08:00")
        start, end = calculate_review_window(
            "daily", "Asia/Shanghai", boundary_hour=0, now=midnight
        )
        self.assertEqual(start.isoformat(), "2026-08-31T00:00:00+08:00")
        self.assertEqual(end.isoformat(), "2026-09-01T00:00:00+08:00")

        before_late_boundary = datetime.fromisoformat("2026-09-01T22:59:00+08:00")
        start, end = calculate_review_window(
            "daily", "Asia/Shanghai", boundary_hour=23, now=before_late_boundary
        )
        self.assertEqual(start.isoformat(), "2026-08-30T23:00:00+08:00")
        self.assertEqual(end.isoformat(), "2026-08-31T23:00:00+08:00")

    def test_weekly_and_daily_use_local_wall_clock_across_dst(self) -> None:
        spring = datetime.fromisoformat("2026-03-09T07:59:00-04:00")
        start, end = calculate_review_window("daily", "America/New_York", now=spring)
        self.assertEqual(start.isoformat(), "2026-03-07T08:00:00-05:00")
        self.assertEqual(end.isoformat(), "2026-03-08T08:00:00-04:00")

        fall = datetime.fromisoformat("2026-11-02T08:00:00-05:00")
        start, end = calculate_review_window("weekly", "America/New_York", now=fall)
        self.assertEqual(start.isoformat(), "2026-10-26T08:00:00-04:00")
        self.assertEqual(end.isoformat(), "2026-11-02T08:00:00-05:00")

    def test_dst_gap_advances_and_overlap_uses_first_boundary(self) -> None:
        spring = datetime.fromisoformat("2026-03-09T02:00:00-04:00")
        start, end = calculate_review_window(
            "daily", "America/New_York", boundary_hour=2, now=spring
        )
        self.assertEqual(start.isoformat(), "2026-03-08T03:00:00-04:00")
        self.assertEqual(end.isoformat(), "2026-03-09T02:00:00-04:00")

        fall = datetime.fromisoformat("2026-11-02T01:00:00-05:00")
        start, end = calculate_review_window(
            "daily", "America/New_York", boundary_hour=1, now=fall
        )
        self.assertEqual(start.isoformat(), "2026-11-01T01:00:00-04:00")
        self.assertEqual(start.fold, 0)
        self.assertEqual(end.isoformat(), "2026-11-02T01:00:00-05:00")

    def test_all_mode_scaffolds_pass_the_existing_report_contract(self) -> None:
        generated = datetime.fromisoformat("2026-09-01T08:01:00+08:00")
        audit = build_review_scaffold(
            "audit", "selected-target", "Asia/Shanghai",
            start="2026-08-31T08:00:00+08:00", end="2026-09-01T08:00:00+08:00",
            generated_at=generated,
        )
        daily = build_daily_scaffold(
            "recent-projects", "Asia/Shanghai", now=generated, generated_at=generated
        )
        weekly = build_weekly_scaffold(
            "recent-projects", "Asia/Shanghai", now=generated, generated_at=generated
        )
        for scaffold in (audit, daily, weekly):
            with self.subTest(scaffold=scaffold.splitlines()[3]):
                self.assertEqual([], check_text(scaffold))
                self.assertIn("authorization: analysis-only", scaffold)
                self.assertIn("source_count: 0", scaffold)

    def test_daily_and_weekly_scaffolds_keep_distinct_mode_templates(self) -> None:
        generated = datetime.fromisoformat("2026-09-01T08:01:00+08:00")
        daily = build_daily_scaffold(
            "recent-projects", "Asia/Shanghai", now=generated, generated_at=generated
        )
        weekly = build_weekly_scaffold(
            "recent-projects", "Asia/Shanghai", now=generated, generated_at=generated
        )

        daily_sections = (
            "## Verified outcomes",
            "## Incomplete work",
            "## Problems found",
            "## Previous changes",
            "## Candidate improvements",
            "## One next action",
            "## Read scope and unknowns",
        )
        weekly_sections = (
            "## Period trend",
            "## Improvement outcomes",
            "## Repeated problems and carry-over",
            "## Candidate state and preservation",
            "## Maintenance health",
            "## GitHub and industry",
            "## Next period",
            "## Read scope and unknowns",
        )
        for report, sections in ((daily, daily_sections), (weekly, weekly_sections)):
            positions = [report.index(section) for section in sections]
            self.assertEqual(positions, sorted(positions))
            self.assertNotIn("# Project goal", report)
            self.assertNotIn("## Overall project progress:", report)
            self.assertRegex(
                report,
                r"(?s)do not prepend the routine\s+Jarvis project card",
            )
        self.assertIn("## One next action", daily)
        self.assertNotIn("## Next period", daily)
        self.assertIn("## Next period", weekly)
        self.assertNotIn("## One next action", weekly)

    def test_review_gate_rejects_missing_duplicate_and_reordered_mode_sections(self) -> None:
        generated = datetime.fromisoformat("2026-09-01T08:01:00+08:00")
        report = build_daily_scaffold(
            "recent-projects", "Asia/Shanghai", now=generated, generated_at=generated
        )
        missing = report.replace(
            "## Candidate improvements\n\n", "Candidate improvements\n\n", 1
        )
        findings = check_text(missing)
        self.assertTrue(any("missing section" in finding for finding in findings))

        duplicate = report.replace(
            "## Candidate improvements\n\n",
            "## Candidate improvements\n\nCandidate only.\n\n## Candidate improvements\n\n",
            1,
        )
        findings = check_text(duplicate)
        self.assertTrue(any("duplicate required section" in finding for finding in findings))

        previous = report.index("## Previous changes")
        candidates = report.index("## Candidate improvements")
        reordered = (
            report[:previous]
            + report[candidates:report.index("## One next action")]
            + report[previous:candidates]
            + report[report.index("## One next action"):]
        )
        findings = check_text(reordered)
        self.assertIn("daily required sections are out of order", findings)

    def test_packaged_daily_and_weekly_templates_keep_the_same_distinct_orders(self) -> None:
        expected = {
            "daily-review.md": (
                "## Verified outcomes",
                "## Incomplete work",
                "## Problems found",
                "## Previous changes",
                "## Candidate improvements",
                "## One next action",
                "## Read scope and unknowns",
            ),
            "daily-review.zh-CN.md": (
                "## 已核实结果",
                "## 未完成工作",
                "## 发现的问题",
                "## 先前改动",
                "## 候选优化",
                "## 唯一下一步",
                "## 读取范围与未知",
            ),
            "weekly-review.md": (
                "## Period trend",
                "## Improvement outcomes",
                "## Repeated problems and carry-over",
                "## Candidate state and preservation",
                "## Maintenance health",
                "## GitHub and industry",
                "## Next period",
                "## Read scope and unknowns",
            ),
            "weekly-review.zh-CN.md": (
                "## 周期趋势",
                "## 优化结果",
                "## 重复问题与延续事项",
                "## 候选状态与保留项",
                "## 维护健康度",
                "## GitHub 与行业",
                "## 下一周期",
                "## 读取范围与未知",
            ),
        }
        for filename, sections in expected.items():
            text = (self.ROOT / "templates" / filename).read_text(encoding="utf-8")
            positions = [text.index(section) for section in sections]
            self.assertEqual(positions, sorted(positions), filename)
            self.assertNotIn("# Project goal", text)
            self.assertNotIn("# 项目总目标", text)

    def test_explicit_windows_remain_available_for_daily_and_weekly(self) -> None:
        generated = datetime.fromisoformat("2026-09-01T08:01:00+08:00")
        scaffold = build_daily_scaffold(
            "selected-target", "Asia/Shanghai",
            start="2026-08-15T07:00:00+08:00", end="2026-08-16T07:00:00+08:00",
            generated_at=generated,
        )
        self.assertIn("coverage: 2026-08-15T07:00:00+08:00 -> 2026-08-16T07:00:00+08:00", scaffold)
        self.assertEqual([], check_text(scaffold))

    def test_invalid_mode_boundary_now_and_partial_explicit_window_fail(self) -> None:
        invalid = (
            lambda: calculate_review_window("audit", "Etc/UTC"),
            lambda: calculate_review_window("daily", "Etc/UTC", boundary_hour=-1),
            lambda: calculate_review_window("daily", "Etc/UTC", boundary_hour=True),
            lambda: calculate_review_window("daily", "Etc/UTC", now=datetime(2026, 1, 1, 8)),
            lambda: build_daily_scaffold("target", "Etc/UTC", start="2026-01-01T00:00:00+00:00"),
            lambda: build_review_scaffold("unknown", "target", "Etc/UTC"),
            lambda: build_daily_scaffold("x" * 513, "Etc/UTC"),
            lambda: build_daily_scaffold("target\u202e", "Etc/UTC"),
            lambda: build_daily_scaffold("left\u2028right", "Etc/UTC"),
            lambda: build_daily_scaffold("left\u2029right", "Etc/UTC"),
            lambda: build_daily_scaffold(" target", "Etc/UTC"),
        )
        for action in invalid:
            with self.subTest(action=action):
                with self.assertRaises(ReviewInputError):
                    action()


if __name__ == "__main__":
    unittest.main()
