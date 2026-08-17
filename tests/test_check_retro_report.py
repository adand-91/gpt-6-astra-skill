#!/usr/bin/env python3
"""Tests for the retrospective checker."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_retro_report import check, claims, labels_in, section_of  # noqa: E402

GOOD = """---
window: 2026-08-10T08:00:00+08:00 .. 2026-08-17T08:00:00+08:00
---

# Retrospective

## Measured

- sessions 23, tool calls 785 (facts)

## Real requirement

- 「别每次都问我」 — 2026-08-14T21:12+08:00 `SAID`
- the acceptance test was never stated `UNKNOWN`

## Requirement trail

| # | Requirement | Ended as | Evidence |
|---|---|---|---|
| 1 | export csv | `DONE` | /tmp/out.csv |

## Mistakes

| Cost | What happened | Layer | Fix |
|---|---|---|---|
| 0 | flake | `ONE-OFF` | none |
| 20 turns (facts) | wrong format assumed | `NO RULE` | write it |

## Automation

| Repeats | Pattern | Verdict | Why |
|---|---|---|---|
| 13x (facts) | rebuild by hand | script | no judgement |

## Not done

- who owns the deploy key `UNKNOWN`

## Next single action

Ask for the acceptance test.
"""


def swap(text: str, old: str, new: str) -> str:
    assert old in text
    return text.replace(old, new)


class TestShippedTemplates(unittest.TestCase):
    def test_retro_template_validates(self) -> None:
        text = (ROOT / "templates" / "retro-report.md").read_text(encoding="utf-8")
        findings, _ = check(text)
        self.assertEqual(findings, [])

    def test_good_report_validates(self) -> None:
        findings, counts = check(GOOD)
        self.assertEqual(findings, [])
        self.assertEqual(counts["sections"], 7)


class TestWindow(unittest.TestCase):
    def test_missing_window_is_reported(self) -> None:
        findings, _ = check(GOOD.replace("window: 2026-08-10T08:00:00+08:00 .. "
                                         "2026-08-17T08:00:00+08:00", "scope: x"))
        self.assertTrue(any("window" in f for f in findings), findings)

    def test_window_without_offset_is_reported(self) -> None:
        findings, _ = check(swap(GOOD, "2026-08-10T08:00:00+08:00 .. 2026-08-17T08:00:00+08:00",
                                 "2026-08-10 .. 2026-08-17"))
        self.assertTrue(any("offset" in f for f in findings), findings)


class TestSections(unittest.TestCase):
    def test_missing_section_is_reported(self) -> None:
        findings, _ = check(swap(GOOD, "## Mistakes", "## Something else"))
        self.assertTrue(any("mistakes" in f for f in findings), findings)

    def test_empty_section_is_reported(self) -> None:
        findings, _ = check(swap(GOOD, "Ask for the acceptance test.\n", ""))
        self.assertTrue(any("no content" in f for f in findings), findings)

    def test_prose_only_section_is_not_empty(self) -> None:
        # Regression: 'Next single action' is a sentence, not a bullet.
        findings, _ = check(GOOD)
        self.assertFalse(any("no content" in f for f in findings), findings)

    def test_chinese_section_names_are_recognised(self) -> None:
        self.assertEqual(section_of("## 真需求"), "real_requirement")
        self.assertEqual(section_of("## 错误"), "mistakes")
        self.assertEqual(section_of("## 可自动化候选"), "automation")
        self.assertEqual(section_of("## 下一步"), "next")


class TestSources(unittest.TestCase):
    def test_number_without_source_is_reported(self) -> None:
        findings, _ = check(swap(GOOD, "sessions 23, tool calls 785 (facts)",
                                 "sessions 23, tool calls 785"))
        self.assertTrue(any("no source" in f for f in findings), findings)

    def test_short_date_counts_as_a_source(self) -> None:
        findings, _ = check(swap(GOOD, "「别每次都问我」 — 2026-08-14T21:12+08:00 `SAID`",
                                 "「又得我提醒你」×3, 08-12 / 08-14 / 08-16 `SAID`"))
        self.assertEqual(findings, [])

    def test_table_row_index_is_not_a_claimed_number(self) -> None:
        # Regression: '| 1 | ... |' must not demand provenance for the number one.
        found, _ = claims("## Requirement trail\n| 1 | export csv | `DONE` | prose only |\n")
        self.assertTrue(all(not c.strip().startswith("1 |") for _, c in found), found)

    def test_zero_cost_cell_needs_no_source(self) -> None:
        findings, _ = check(GOOD)
        self.assertFalse(any("flake" in f for f in findings), findings)

    def test_vague_quantity_without_measurement_is_reported(self) -> None:
        findings, _ = check(swap(GOOD, "| 13x (facts) | rebuild by hand | script | no judgement |",
                                 "| some | most of the session was rebuilds | script | none |"))
        self.assertTrue(any("quantity" in f for f in findings), findings)


class TestLabels(unittest.TestCase):
    def test_unlabelled_requirement_claim_is_reported(self) -> None:
        findings, _ = check(swap(GOOD, "- the acceptance test was never stated `UNKNOWN`",
                                 "- the acceptance test was never stated"))
        self.assertTrue(any("no SAID" in f or "label" in f for f in findings), findings)

    def test_labels_in_both_languages(self) -> None:
        self.assertEqual(labels_in("他说 `原话`"), ["SAID"])
        self.assertEqual(labels_in("my reading `INFERRED`"), ["INFERRED"])
        self.assertEqual(labels_in("no record `未知`"), ["UNKNOWN"])

    def test_lowercase_prose_is_not_a_label(self) -> None:
        self.assertEqual(labels_in("the user said it was inferred from context"), [])


class TestChinese(unittest.TestCase):
    def test_chinese_report_validates_with_chinese_findings(self) -> None:
        text = """---
window: 2026-08-10T08:00:00+08:00 .. 2026-08-17T08:00:00+08:00
---

# 复盘

## 实测

- 会话 23 个 工具调用 785 次 (facts)

## 真需求

- 「别每次都问我」 2026-08-14T21:12+08:00 `原话`

## 需求去向

- 导出 csv `已完成` /tmp/out.csv `推断`

## 错误

- 假设了错误的格式 20 轮 (facts) `推断`

## 可自动化

- 手工重建 13次 (facts) `推断`

## 未完成

- 部署密钥归谁 `未知`

## 下一步

问出验收动作。
"""
        findings, _ = check(text, lang="zh")
        self.assertEqual(findings, [])

    def test_chinese_findings_are_chinese(self) -> None:
        findings, _ = check("# 复盘\n## 实测\n- 跑了 47 次\n", lang="zh")
        self.assertTrue(any("没有出处" in f or "没有窗口" in f for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
