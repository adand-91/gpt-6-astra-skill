from __future__ import annotations

import unittest

from scripts.check_jarvis_report import check_text


def project(progress="60", area="40", bar="██████░░░░"):
    return f"""# 项目总目标

完成 Jarvis 接管验收。

## 项目总进度：约 {progress}%（实测，依据：测试结果）

{bar}

项目阶段：接管行为回归。
当前工作区域：格式检查。

## 当前区域进度：约 {area}%（估算，依据：里程碑权重）

████░░░░░░

当前卡点：当前无阻断问题。
你现在无需操作。

# 下一步

运行回归。
用途：验证报告格式。
交付：测试结果。
完成标准：四类请求通过。
下次汇报：测试完成后。
"""


class JarvisReportFormatTests(unittest.TestCase):
    def test_valid_project(self):
        self.assertEqual([], check_text(project()))

    def test_missing_overall_progress_is_rejected(self):
        self.assertTrue(any("项目总进度" in x for x in check_text(project().replace("## 项目总进度：约 60%（实测，依据：测试结果）\n\n██████░░░░\n\n", ""))))

    def test_nine_cells_and_overall_substitution_fail(self):
        bad = project(bar="█████░░░░")
        self.assertTrue(any("10" in x for x in check_text(bad)))
        overall_ok_but_area_wrong = project(area="100")
        self.assertTrue(any("area progress" in x for x in check_text(overall_ok_but_area_wrong)))

    def test_unlocked_scope_cannot_invent_percent(self):
        bad = project().replace("## 项目总进度：约 60%（实测，依据：测试结果）\n\n██████░░░░", "## 项目总进度\n\n范围未锁定，无法计算\n\n60%\n\n██████░░░░")
        self.assertTrue(any("unlocked" in x for x in check_text(bad)))

    def test_next_step_fields_are_required(self):
        bad = project().replace("用途：验证报告格式。\n", "")
        self.assertTrue(any("用途" in x for x in check_text(bad)))

    def test_daily_and_weekly_are_ordered_and_distinct(self):
        daily = "\n\n".join(f"## {x}\n\n内容。" for x in ("已核实结果", "未完成工作", "发现的问题", "先前改动", "候选优化", "唯一下一步", "读取范围与未知"))
        self.assertEqual([], check_text(daily, "daily"))
        self.assertTrue(check_text(daily.replace("## 候选优化", "## 已核实结果"), "daily"))
        self.assertTrue(any("must not be mixed" in x for x in check_text(daily + "\n\n# 项目总目标\n\nX", "daily")))

    def test_code_fence_is_not_a_report(self):
        self.assertTrue(any("code fences" in x for x in check_text("```\n" + project() + "\n```")))


if __name__ == "__main__":
    unittest.main()
