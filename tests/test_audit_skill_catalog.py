from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_skill_catalog.py"
SPEC = importlib.util.spec_from_file_location("audit_skill_catalog", SCRIPT)
assert SPEC and SPEC.loader
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


def skill(description: str, body: str = "") -> str:
    return f"---\nname: sample\n{description}\n---\n{body}"


class AuditSkillCatalogTests(unittest.TestCase):
    def test_multiline_plain_description_is_not_truncated_into_a_pass(self) -> None:
        source = skill("description: review documents\n  " + "long continuation " * 30,
                       "Input output check scope")
        result = catalog.audit(self._write_skill(source))
        self.assertEqual(result["status"], "REVIEW")
        self.assertIn("description_manual_review", result["findings"])
        self.assertNotIn("missing_description", result["findings"])

    def test_recognizes_inline_and_quoted_descriptions(self) -> None:
        for value, expected in (
            ("description: concise description", "concise description"),
            ('description: "double quoted"', "double quoted"),
            ("description: 'single quoted'", "single quoted"),
        ):
            with self.subTest(value=value):
                self.assertEqual(catalog.description(skill(value)), (expected, "ok"))

    def test_recognizes_folded_and_literal_descriptions(self) -> None:
        for header, expected in (
            (">", "first line second line"),
            (">-", "first line second line"),
            ("|", "first line\nsecond line"),
            ("|-", "first line\nsecond line"),
        ):
            with self.subTest(header=header):
                source = skill(f"description: {header}\n  first line\n  second line")
                self.assertEqual(catalog.description(source), (expected, "ok"))

    def test_special_scalars_and_yaml_structures_need_manual_review(self) -> None:
        for value in (
            "description: [one, two]",
            "description: {one: two}",
            "description: &anchor",
            "description: null",
            "description: plain # comment",
            "description: text: uncertain",
        ):
            with self.subTest(value=value):
                self.assertEqual(catalog.description(skill(value)), ("", "manual_review"))

    def test_block_description_stops_at_next_metadata_field(self) -> None:
        source = "---\ndescription: >\n  first line\n  second line\nname: sample\n---\n"
        self.assertEqual(catalog.description(source), ("first line second line", "ok"))
        self.assertNotIn("missing_name", catalog.audit(self._write_skill(source))["findings"])

    def test_duplicate_descriptions_need_manual_review(self) -> None:
        source = "---\nname: sample\ndescription: one\ndescription: two\n---\n"
        result = catalog.audit(self._write_skill(source))
        self.assertIn("description_manual_review", result["findings"])
        self.assertNotIn("missing_description", result["findings"])

    def test_only_reads_frontmatter_fields(self) -> None:
        source = "# Heading\nname: body-name\ndescription: body description\n"
        result = catalog.audit(self._write_skill(source))
        self.assertIn("missing_frontmatter", result["findings"])
        self.assertIn("missing_name", result["findings"])
        self.assertIn("missing_description", result["findings"])

    def test_preamble_and_unclosed_frontmatter_do_not_count_fields(self) -> None:
        for source in (
            "Preamble\n---\nname: body-name\ndescription: body description\n---\n",
            "---\nname: sample\ndescription: unfinished\n",
        ):
            with self.subTest(source=source):
                result = catalog.audit(self._write_skill(source))
                self.assertIn("missing_frontmatter", result["findings"])
                self.assertIn("missing_name", result["findings"])
                self.assertIn("missing_description", result["findings"])

    def test_empty_or_ambiguous_description_is_not_false_missing(self) -> None:
        empty = catalog.audit(self._write_skill("---\n---\n"))
        ambiguous = catalog.audit(self._write_skill(skill("description: >  # unsupported form")))
        self.assertIn("missing_name", empty["findings"])
        self.assertIn("missing_description", empty["findings"])
        self.assertIn("description_manual_review", ambiguous["findings"])
        self.assertNotIn("missing_description", ambiguous["findings"])

    def test_no_matching_input_exits_with_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            previous = sys.argv
            sys.argv = [str(SCRIPT), directory]
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        catalog.main()
            finally:
                sys.argv = previous
        self.assertEqual(raised.exception.code, 2)

    def test_length_review_and_json_explain_the_local_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "SKILL.md"
            source.write_text(skill(f"description: {'a' * 421}"), encoding="utf-8")
            report = root / "report.json"
            previous = sys.argv
            sys.argv = [str(SCRIPT), str(source), "--json", str(report)]
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(catalog.main(), 0)
            finally:
                sys.argv = previous
            payload = json.loads(report.read_text(encoding="utf-8"))
        self.assertIn("description_length_review", payload["results"][0]["findings"])
        self.assertIn("local readability heuristic", payload["description_length_threshold"])
        self.assertIn("not an OpenAI requirement", payload["description_length_threshold"])

    def _write_skill(self, content: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "SKILL.md"
        path.write_text(content, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
