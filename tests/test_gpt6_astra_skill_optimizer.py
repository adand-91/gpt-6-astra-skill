from __future__ import annotations

import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "gpt6-astra-skill-optimizer"
SKILL = PLUGIN / "skills" / "gpt6-astra-skill-optimizer"


class AstraSkillOptimizerTests(unittest.TestCase):
    def test_manifest_is_independent_skill_only_v1(self) -> None:
        manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "gpt6-astra-skill-optimizer")
        self.assertEqual(manifest["version"], "1.0.2")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["interface"]["capabilities"], ["Interactive"])
        self.assertEqual(len(manifest["interface"]["defaultPrompt"]), 3)
        self.assertTrue(all(len(p) <= 128 for p in manifest["interface"]["defaultPrompt"]))
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("hooks", manifest)

    def test_local_marketplace_exposes_independent_plugin(self) -> None:
        standalone = json.loads((ROOT / ".agents/plugins/gpt6-astra-marketplace.json").read_text())
        self.assertEqual(standalone["plugins"][0]["name"], "gpt6-astra-skill-optimizer")

    def test_skill_has_joint_audit_and_authority_boundary(self) -> None:
        text = (SKILL / "SKILL.md").read_text()
        for phrase in ("independent Skill audit", "does not", "train GPT-6 Astra",
                       "read-only audit", "项目", "Skill", "事实", "推断", "未知",
                       "联合审计", "prompt-injection", "exact path allowlist"):
            self.assertIn(phrase, text)
        order = [text.index(x) for x in ("## Entry and authority", "## Evidence contract",
                                         "## Joint audit procedure", "## Required report",
                                         "## Safety boundaries")]
        self.assertEqual(order, sorted(order))

    def test_sources_and_cases_are_release_ready_shape(self) -> None:
        sources = (SKILL / "references" / "official-sources.md").read_text()
        for url in ("latest-model", "tools-skills", "plugins/concepts/skills",
                    "plugins/app-guidelines", "plugins/deploy/submission"):
            self.assertIn(url, sources)
        cases = (SKILL / "references" / "test-cases.md").read_text()
        positive, negative = cases.split("## Negative and boundary", 1)
        self.assertGreaterEqual(len(re.findall(r"^\d+\. ", positive, re.M)), 5)
        self.assertGreaterEqual(len(re.findall(r"^\d+\. ", negative, re.M)), 3)
        self.assertIn("does not train GPT-6 Astra", (PLUGIN / "README.md").read_text())

    def test_fixed_delta_contract_and_domain_dimensions(self) -> None:
        text = (SKILL / "SKILL.md").read_text()
        for phrase in ("优化前", "当前问题", "优化后", "验证方式", "唯一下一步",
                       "platform costs", "重估触发", "业务状态", "execution receipts", "短代码块"):
            self.assertIn(phrase, text)
        schema = (SKILL / "references" / "audit-schema.md").read_text()
        for dimension in ("pricing", "communication", "state", "execution"):
            self.assertIn(dimension, schema)

    def test_domain_regression_cases_present(self) -> None:
        cases = (SKILL / "references" / "test-cases.md").read_text()
        for phrase in ("platform fee was added", "2–3 short", "业务状态", "understanding receipt",
                       "silently passed through", "claim completion"):
            self.assertIn(phrase, cases)

    def test_no_second_runtime_or_private_evidence_fixture(self) -> None:
        self.assertEqual(list(PLUGIN.rglob("*.py")), [])
        self.assertFalse((PLUGIN / ".mcp.json").exists())
        self.assertFalse((PLUGIN / "hooks").exists())


if __name__ == "__main__":
    unittest.main()
