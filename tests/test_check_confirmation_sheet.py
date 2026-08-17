#!/usr/bin/env python3
"""Tests for the confirmation-sheet checker."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_confirmation_sheet import check, is_locked, labels_in, normalise, parse  # noqa: E402

MINIMAL = """
**Goal**
- Ship a thing. `CONFIRMED`

**In scope**
- The thing. `CONFIRMED`

**Out of scope**
- The other thing. `CONFIRMED`

**Inputs**
- `/tmp/sample.csv`. `CONFIRMED`

**Outputs**
- `/tmp/out.xlsx`. `CONFIRMED`

**Acceptance**
- Run it, see the file. `CONFIRMED`

**Constraints**
- By Friday. `CONFIRMED`

**Where it runs**
- This laptop, macOS. `CONFIRMED`

**Open items**
- Nothing outstanding. `CONFIRMED`

Locked: yes — 2026-08-17, confirmed by user
"""


def without(section: str) -> str:
    """Drop one field block from MINIMAL."""
    blocks = MINIMAL.strip().split("\n\n")
    return "\n\n".join(b for b in blocks if not b.startswith(f"**{section}**"))


class TestShippedFiles(unittest.TestCase):
    def test_english_template_validates(self) -> None:
        text = (ROOT / "templates" / "confirmation-sheet.md").read_text(encoding="utf-8")
        self.assertEqual(check(text), [])

    def test_chinese_template_validates(self) -> None:
        text = (ROOT / "templates" / "confirmation-sheet.zh-CN.md").read_text(encoding="utf-8")
        self.assertEqual(check(text, lang="zh"), [])


class TestFields(unittest.TestCase):
    def test_minimal_sheet_is_valid(self) -> None:
        self.assertEqual(check(MINIMAL), [])

    def test_missing_field_is_reported(self) -> None:
        findings = check(without("Acceptance"))
        self.assertTrue(any("acceptance" in f for f in findings), findings)

    def test_field_with_no_items_is_reported(self) -> None:
        text = MINIMAL.replace("- By Friday. `CONFIRMED`\n", "")
        findings = check(text)
        self.assertTrue(any("constraints" in f for f in findings), findings)

    def test_all_nine_fields_are_parsed(self) -> None:
        sections, _ = parse(MINIMAL)
        self.assertEqual(len(sections), 9)

    def test_out_of_scope_wins_over_in_scope(self) -> None:
        sections, _ = parse(MINIMAL)
        self.assertEqual(sections["out_of_scope"], ["The other thing. `CONFIRMED`"])
        self.assertEqual(sections["in_scope"], ["The thing. `CONFIRMED`"])


class TestLabels(unittest.TestCase):
    def test_unlabelled_item_is_reported(self) -> None:
        findings = check(MINIMAL.replace("- The thing. `CONFIRMED`", "- The thing."))
        self.assertTrue(any("no label" in f for f in findings), findings)

    def test_double_label_is_reported(self) -> None:
        findings = check(
            MINIMAL.replace("- The thing. `CONFIRMED`", "- The thing. `CONFIRMED` `INFERRED`")
        )
        self.assertTrue(any("2 labels" in f for f in findings), findings)

    def test_confirmed_and_open_are_distinct_in_chinese(self) -> None:
        self.assertEqual(labels_in("做完了。`已确认`"), ["CONFIRMED"])
        self.assertEqual(labels_in("还没定。`待确认`"), ["OPEN"])
        self.assertEqual(labels_in("我先定了。`AI推断`"), ["INFERRED"])

    def test_label_needs_a_word_boundary_in_english(self) -> None:
        self.assertEqual(labels_in("this reopened the question"), [])

    def test_lowercase_prose_is_not_a_label(self) -> None:
        # Regression: "run X, open Y, see Z" is an acceptance action, not an OPEN item.
        self.assertEqual(labels_in("Run it, open the file, see the rows. `CONFIRMED`"),
                         ["CONFIRMED"])


class TestOpenItems(unittest.TestCase):
    def test_open_item_must_name_an_owner(self) -> None:
        findings = check(MINIMAL.replace("- `/tmp/sample.csv`. `CONFIRMED`", "- A sample. `OPEN`"))
        self.assertTrue(any("who owes" in f for f in findings), findings)

    def test_open_elsewhere_must_be_listed(self) -> None:
        text = MINIMAL.replace(
            "- `/tmp/sample.csv`. `CONFIRMED`", "- A sample. `OPEN` — owner: user"
        )
        findings = check(text)
        self.assertTrue(any("lists none" in f for f in findings), findings)

    def test_open_elsewhere_satisfied_by_listing(self) -> None:
        text = MINIMAL.replace(
            "- `/tmp/sample.csv`. `CONFIRMED`", "- A sample. `OPEN` — owner: user"
        ).replace("- Nothing outstanding. `CONFIRMED`", "- The sample. `OPEN` — owner: user")
        self.assertEqual(check(text), [])


class TestLock(unittest.TestCase):
    def test_missing_lock_line_is_reported(self) -> None:
        text = MINIMAL.replace("Locked: yes — 2026-08-17, confirmed by user", "")
        findings = check(text)
        self.assertTrue(any("Locked:" in f for f in findings), findings)

    def test_lock_state_is_read(self) -> None:
        _, value = parse(MINIMAL)
        self.assertTrue(is_locked(value))

    def test_unlocked_sheet_is_valid_but_not_locked(self) -> None:
        text = MINIMAL.replace(
            "Locked: yes — 2026-08-17, confirmed by user", "Locked: no — awaiting user"
        )
        self.assertEqual(check(text), [])
        _, value = parse(text)
        self.assertFalse(is_locked(value))

    def test_chinese_lock_line_is_read(self) -> None:
        _, value = parse("锁定：是 —— 2026-08-17，用户已确认")
        self.assertTrue(value.startswith("是"))


class TestPromotion(unittest.TestCase):
    def setUp(self) -> None:
        self.old = MINIMAL.replace("- The thing. `CONFIRMED`", "- The thing. `INFERRED`")

    def test_silent_promotion_is_reported(self) -> None:
        findings = check(MINIMAL, baseline=self.old)
        self.assertTrue(any("without a recorded confirmation" in f for f in findings), findings)

    def test_approved_promotion_passes(self) -> None:
        self.assertEqual(check(MINIMAL, baseline=self.old, promotions_approved=True), [])

    def test_unchanged_labels_are_not_promotions(self) -> None:
        self.assertEqual(check(MINIMAL, baseline=MINIMAL), [])

    def test_normalise_ignores_labels_and_markup(self) -> None:
        self.assertEqual(
            normalise("- Output as CSV. `INFERRED`"), normalise("Output as CSV. `CONFIRMED`")
        )


class TestSize(unittest.TestCase):
    def test_oversized_sheet_is_reported(self) -> None:
        findings = check(MINIMAL, max_bytes=100)
        self.assertTrue(any("one-screen budget" in f for f in findings), findings)


class TestChinese(unittest.TestCase):
    def test_chinese_sheet_validates_with_chinese_messages(self) -> None:
        text = """
**目标**
- 交一个东西。`已确认`

**包含**
- 那个东西。`已确认`

**不包含**
- 另一个东西。`已确认`

**输入**
- `/tmp/sample.csv`。`已确认`

**输出**
- `/tmp/out.xlsx`。`已确认`

**验收**
- 跑一下，看到文件。`已确认`

**约束**
- 周五之前。`已确认`

**执行位置**
- 这台笔记本，macOS。`已确认`

**未确认项**
- 没有了。`已确认`

锁定：是 —— 2026-08-17，用户已确认
"""
        self.assertEqual(check(text, lang="zh"), [])

    def test_chinese_findings_are_chinese(self) -> None:
        findings = check("**目标**\n- 交一个东西。`已确认`\n锁定：是", lang="zh")
        self.assertTrue(any("缺少必备字段" in f for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
