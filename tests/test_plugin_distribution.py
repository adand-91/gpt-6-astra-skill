from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

from requirement_ledger import __version__


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "requirement-ledger"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"


def plugin_version(python_version: str) -> str:
    match = re.fullmatch(r"(\d+\.\d+\.\d+)(?:(a|b|rc)(\d+))?", python_version)
    if match is None:
        raise AssertionError(f"unsupported Python package version: {python_version}")
    base, phase, number = match.groups()
    labels = {"a": "alpha", "b": "beta", "rc": "rc"}
    return base if phase is None else f"{base}-{labels[phase]}.{number}"


class PluginDistributionTests(unittest.TestCase):
    def setUp(self) -> None:
        if not PLUGIN.exists():
            self.skipTest("the Codex plugin is a separate repository distribution layer")

    def test_manifest_and_marketplace_resolve_the_legacy_skill_plugin(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "requirement-ledger")
        self.assertEqual(manifest["version"], plugin_version(__version__))
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["interface"]["capabilities"], ["Interactive"])
        self.assertEqual(len(manifest["interface"]["defaultPrompt"]), 3)
        self.assertTrue(
            all(len(prompt) <= 128 for prompt in manifest["interface"]["defaultPrompt"])
        )
        self.assertIn("Codex-first", manifest["description"])
        self.assertIn("project manager", manifest["description"])
        self.assertIn("programming newcomers", manifest["description"])
        self.assertIn("evidence-bound", manifest["description"])
        self.assertIn("Hi Jarvis, take over this Codex project", manifest["interface"]["defaultPrompt"][0])
        self.assertIn("one clear next action", manifest["interface"]["defaultPrompt"][0])
        self.assertIn("requirement change or blocker", manifest["interface"]["defaultPrompt"][1])
        self.assertIn("plain language", manifest["interface"]["defaultPrompt"][1])
        self.assertIn("evidence-bound", manifest["interface"]["defaultPrompt"][2])
        self.assertIn("three answer depths", manifest["interface"]["longDescription"])
        self.assertIn("dedicated daily and weekly reports", manifest["interface"]["longDescription"])
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        self.assertNotIn("hooks", manifest)

        self.assertEqual(marketplace["name"], "requirement-ledger-local")
        entry = next(entry for entry in marketplace["plugins"] if entry["name"] == manifest["name"])
        self.assertEqual(entry["name"], manifest["name"])
        resolved = MARKETPLACE.parents[2] / entry["source"]["path"]
        self.assertEqual(resolved.resolve(), PLUGIN.resolve())

    def test_plugin_has_no_second_runtime_or_permission_surface(self) -> None:
        forbidden = (
            PLUGIN / ".mcp.json",
            PLUGIN / ".app.json",
            PLUGIN / "hooks",
            PLUGIN / "src",
            PLUGIN / "tests",
        )
        self.assertTrue(all(not path.exists() for path in forbidden))
        python_files = list(PLUGIN.rglob("*.py"))
        self.assertEqual(python_files, [])

    def test_skill_is_focused_and_carries_positive_and_negative_cases(self) -> None:
        skill_root = PLUGIN / "skills" / "requirement-ledger-workflow"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        cli_workflows = (skill_root / "references" / "cli-workflows.md").read_text(
            encoding="utf-8"
        )
        cases = (skill_root / "references" / "test-cases.md").read_text(encoding="utf-8")
        readmes = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("README.md", "README.zh-CN.md")
        )
        self.assertRegex(skill, r"(?s)^---\nname: requirement-ledger-workflow\ndescription: .+?\n---")
        frontmatter = skill.split("---", 2)[1]
        for trigger in ("Jarvis/贾维斯", "接管这个项目", "汇报一下项目进度"):
            self.assertIn(trigger, frontmatter)
        self.assertIn("including any required Skill-use announcement, must begin exactly `可以接管。`", frontmatter)
        self.assertIn("must be exactly `可以汇报。`", frontmatter)
        self.assertIn("bounded status answer, not a new audit or Worker task", frontmatter)
        self.assertIn("do not force every reply into one dashboard", frontmatter)
        self.assertIn("Do not install", skill)
        self.assertIn("source-verify", skill)
        self.assertIn("review-bind", skill)
        self.assertIn("review-handoff-check", skill)
        self.assertIn("Codex host-selected quick audit (unbound)", skill)
        self.assertIn("Evidence-bound CLI review (explicit sources)", skill)
        self.assertIn("host-selected / unbound", skill)
        self.assertIn("Do not run\n`review-init`", skill)
        self.assertIn("do not ask for a time window,\nraw JSONL, scope root, file paths", skill)
        self.assertIn("For v1 `review-init --mode audit`,\nalso require explicit `--start`, `--end`, and an IANA `--timezone`", skill)
        self.assertIn("do not report a source count, completeness, or a\nbinding", skill)
        self.assertIn("in-progress turn", skill)
        self.assertIn("They are entry point B,\nthe evidence-bound CLI review", cli_workflows)
        self.assertIn("does not call `review-init`", cli_workflows)
        self.assertIn("For v1 `audit`, supply explicit `--start`, `--end`, and `--timezone`", cli_workflows)
        self.assertIn("host-selected / unbound", cases)
        self.assertIn("do not call `review-init` or create a source pack", cases)
        self.assertIn("evidence-bound CLI audit still requires explicit start, end, and timezone", cases)
        self.assertIn("已选中的 WQ Alpha 项目", cases)
        self.assertIn("$requirement-ledger-workflow", readmes)
        self.assertIn("Hi Jarvis, take over this selected project", readmes)
        self.assertIn("接管这个已选项目", readmes)
        self.assertIn("uv tool install .", readmes)
        self.assertIn("host-selected / unbound", readmes)
        self.assertIn("evidence-bound", readmes)
        self.assertIn("codex plugin remove requirement-ledger@requirement-ledger-local", readmes)
        self.assertIn("This is not a Claude Code port", readmes)
        positive, negative = cases.split("## Negative and boundary", 1)
        self.assertGreaterEqual(len(re.findall(r"^\d+\. ", positive, re.MULTILINE)), 5)
        self.assertGreaterEqual(len(re.findall(r"^\d+\. ", negative, re.MULTILINE)), 3)

    def test_skill_locks_the_project_steering_report_contract(self) -> None:
        skill_root = PLUGIN / "skills" / "requirement-ledger-workflow"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        cases = (skill_root / "references" / "test-cases.md").read_text(
            encoding="utf-8"
        )

        ordered_fields = (
            "`Project goal` / `项目总目标`",
            "overall project progress and a progress bar",
            "the current work area set by the assistant from that goal",
            "current-area progress and a progress bar",
            "current blocker",
            "what the user needs to decide",
            "exactly one next step",
            "the completion test for that step",
        )
        positions = [skill.index(field) for field in ordered_fields]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("exactly `项目总目标`", skill)
        self.assertIn("do not render all eight as equal large headings", skill)
        self.assertIn("`measured` / `实测`", skill)
        self.assertIn("`estimated` / `估算`", skill)
        self.assertIn("`范围未锁定，无法计算`", skill)
        self.assertIn("`██████░░░░ 约 60%（估算）`", skill)
        self.assertIn("`当前无阻断问题`", skill)
        self.assertIn("`你现在无需操作`", skill)
        self.assertIn("## 项目总进度：约 60%（估算）", skill)
        self.assertIn("当前工作区域：<one active stage derived from the goal>", skill)
        self.assertIn("## 当前区域进度：约 40%（估算）", skill)
        self.assertIn("# 需要你确定", skill)
        self.assertIn("Mandatory Jarvis first screen", skill)
        self.assertLess(
            skill.index("## Mandatory Jarvis first screen"),
            skill.index("## Choose one entry point"),
        )
        self.assertIn("Do not replace the hierarchy with six same-weight bold", skill)
        self.assertIn("Do not invent a competing card or dashboard format", skill)
        self.assertIn("promote only that field to a heading", skill)
        self.assertIn("decision-complete project-steering report", skill)
        self.assertIn("Length follows the complexity of\nthe decision", skill)
        self.assertIn("Do not shorten a report for its own sake", skill)
        self.assertIn("This limit applies\nto suggestions, not supporting evidence", skill)
        self.assertIn("Short sentences and a low word count are not goals", skill)
        self.assertIn("Daily or weekly reports require a separately configured and\nauthorized schedule", skill)
        self.assertIn("Fast takeover first pass", skill)
        self.assertIn("answer before any tool call", skill)
        self.assertIn("before announcing this Skill, a plan, a read, a review, a tool, or", skill)
        self.assertIn("exact fast acknowledgement is the Skill-use announcement", skill)
        self.assertIn("do not apologise for failing the first-visible rule", skill)
        self.assertIn("`可以汇报。` as the complete pre-tool acknowledgement", skill)
        self.assertIn("progress report from the current checkpoint is a bounded status answer", skill)
        self.assertIn("Do not load a routing Skill solely for\nthat answer", skill)
        self.assertIn("read or wait on another task", skill)
        self.assertRegex(skill, r"start a\s+Worker merely to repeat the checkpoint")
        self.assertIn("label that result `unknown` or `unstable`", skill)
        self.assertIn("Before the first report, read at most two checkpoint files", skill)
        self.assertIn("follow its one active pointer", skill)
        self.assertIn("not as permission to browse", skill)
        self.assertIn("Do not open `README`", skill)
        self.assertIn("可以接管。", skill)
        for event in (
            "takes over a selected project",
            "starts a\nbounded task",
            "completes a stage",
            "meets a blocker",
            "detects a plan deviation",
            "receives fresh\nversion-acceptance evidence",
        ):
            self.assertIn(event, skill)

        self.assertIn("Answer depth router", skill)
        self.assertIn("Direct answer", skill)
        self.assertIn("Explained answer", skill)
        self.assertIn("Full project report", skill)
        self.assertIn("Distinct daily and weekly templates", skill)
        self.assertRegex(
            skill,
            r"(?s)Daily and weekly reviews are separate report modes.+?do\s+not prepend",
        )
        self.assertIn("A daily report has one\nhighest-value next action", skill)
        self.assertIn("A weekly report may rank at most three", skill)
        self.assertIn("High-impact evidence escalation", skill)
        self.assertIn("Resource and Skill routing", skill)
        self.assertIn("Feedback-driven improvement", skill)
        self.assertIn("Do not claim passive observation", skill)
        self.assertIn("Daily/weekly report-format regressions", cases)
        self.assertIn("dedicated daily template", cases)
        self.assertIn("dedicated weekly template", cases)
        self.assertIn("Answer-depth regressions", cases)
        self.assertIn("Evidence, resource, and improvement regressions", cases)

        for required_case in (
            "Project-steering report regressions",
            "Normal progress with a fixed project goal",
            "范围未锁定，无法计算",
            "The same ordinary risk first does not block progress",
            "can I publish it?",
            "The user replaces the current project goal",
            "Never add “由你和 AI 共同确定”",
            "do not claim that a daily or weekly report will run unattended",
            "rewrite it as clear active sentences",
            "a shorter answer is not automatically\n   better",
            "不要把“还在跑，先等等”当成完整汇报",
            "嗨，贾维斯，帮我接管这个项目",
            "Jarvis，汇报一下项目进度",
            "self-invented `项目仪表盘`",
            "the first visible reply begins `可以接管。`",
            "The complete pre-tool acknowledgement is exactly `可以汇报。`",
            "do not browse central-context collections or related tasks",
            "Do not call a task reader, wait for the task",
            "这个策略现在能用吗",
            "为什么不能用",
            "完整汇报一下这个项目现在做到哪了",
            "Windows remains untested",
        ):
            self.assertIn(required_case, cases)

    def test_skill_locks_project_state_and_lifecycle_router(self) -> None:
        skill_root = PLUGIN / "skills" / "requirement-ledger-workflow"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        cases = (skill_root / "references" / "test-cases.md").read_text(
            encoding="utf-8"
        )
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        product_contract = (ROOT / "docs" / "V1_PRODUCT_CONTRACT.md").read_text(
            encoding="utf-8"
        )
        product_contract_zh = (
            ROOT / "docs" / "V1_PRODUCT_CONTRACT.zh-CN.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Project state and lifecycle router", skill)
        self.assertIn("Choose exactly one primary scene", skill)
        self.assertIn("Ask no more than three at once", skill)
        self.assertIn("Show the complete six-scene menu only", skill)
        self.assertIn("track the selected target, evidence freshness, current authority", skill)
        self.assertIn("Do not print them as a fixed bilingual metadata", skill)
        self.assertNotIn("Project card / 项目卡：", skill)

        scenes = (
            "Project setup / 首次建档",
            "Progress review / 进度复盘",
            "Requirement change / 需求变化",
            "Blocker diagnosis / 卡点诊断",
            "Version acceptance / 版本验收",
            "Handoff / 换对话交接",
        )
        positions = [skill.index(scene) for scene in scenes]
        self.assertEqual(positions, sorted(positions))

        self.assertIn("Project-card and lifecycle-router regressions", cases)
        self.assertIn("Plain language is not a minimum-word-count target", product_contract)
        self.assertIn("说人话不等于把字数压到最少", product_contract_zh)
        for phrase in (
            "今天这个项目推进了什么",
            "客户把要求改成必须离线运行",
            "项目启动不了",
            "这个版本是不是已经可以发布",
            "生成一份换对话交接",
            "需求改了，顺便验收版本",
        ):
            self.assertIn(phrase, cases)

        self.assertIn("Jarvis v1 product completion contract", product_contract)
        self.assertIn("Six lifecycle scenes", product_contract)
        self.assertIn("贾维斯 v1 产品完工合同", product_contract_zh)
        self.assertIn("six project lifecycle scenes", manifest["interface"]["longDescription"])


if __name__ == "__main__":
    unittest.main()
