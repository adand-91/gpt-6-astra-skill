from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

from requirement_ledger.cli import main
from requirement_ledger.pipeline import analyze_evidence, synthetic_demo_bundle


def make_repo(root: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Synthetic Tester"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "synthetic@example.invalid"], check=True)
    (root / "README.md").write_text("synthetic\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
    return root


class TestCLI(unittest.TestCase):
    def call(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_demo_writes_complete_offline_walkthrough(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "demo"
            code, output, error = self.call(["demo", "--output-dir", str(target)])
            self.assertEqual(code, 0, error)
            self.assertIn("DEMO_COMPLETE", output)
            self.assertEqual(len(list(target.iterdir())), 5)
            report = (target / "04-report.md").read_text(encoding="utf-8")
            self.assertIn("Raw quotes: not included", report)
            validation = json.loads((target / "05-validation.json").read_text(encoding="utf-8"))
            self.assertEqual(validation["result"]["status"], "improved")
            second = Path(tmp) / "demo-second"
            self.assertEqual(self.call(["demo", "--output-dir", str(second)])[0], 0)
            first_bytes = {path.name: path.read_bytes() for path in target.iterdir()}
            second_bytes = {path.name: path.read_bytes() for path in second.iterdir()}
            self.assertEqual(first_bytes, second_bytes)

    def test_cli_scan_analyze_report_and_suggest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = make_repo(base / "repo")
            transcript = base / "transcript.md"
            transcript.write_text("# User\nwrong, keep compatibility\n", encoding="utf-8")
            evidence = base / "evidence.private.json"
            analysis = base / "analysis.json"
            report = base / "report.md"
            proposal = base / "proposal.json"
            code, _, err = self.call(["scan", "--repo", str(repo), "--input", str(transcript),
                                      "--provider", "text", "--output", str(evidence)])
            self.assertEqual(code, 0, err)
            if os.name != "nt":
                self.assertEqual(evidence.stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.call(["analyze", "--evidence", str(evidence),
                                        "--output", str(analysis)])[0], 0)
            self.assertEqual(self.call(["report", "--analysis", str(analysis),
                                        "--output", str(report)])[0], 0)
            self.assertEqual(self.call(["suggest", "--analysis", str(analysis),
                                        "--output", str(proposal)])[0], 0)
            self.assertNotIn("keep compatibility", report.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(proposal.read_text(encoding="utf-8"))["status"],
                             "DRAFT — NOT SENT")

    def test_privacy_check_never_prints_matched_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "canary.txt"
            path.write_text("person@example.test", encoding="utf-8")
            code, output, _ = self.call(["privacy-check", str(path)])
            self.assertEqual(code, 3)
            self.assertIn("email", output)
            self.assertNotIn("person@example.test", output)

    def test_report_privacy_block_happens_before_output_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            analysis = analyze_evidence(synthetic_demo_bundle())
            analysis["issues"][0]["title"] = "Contact person@example.test"
            source = root / "analysis.json"
            target = root / "blocked-report.json"
            source.write_text(json.dumps(analysis), encoding="utf-8")
            with mock.patch("requirement_ledger.pipeline._PUBLIC_TITLES",
                            {"Contact person@example.test"}):
                code, output, error = self.call([
                    "report", "--analysis", str(source), "--output", str(target),
                ])
            self.assertEqual(code, 3)
            self.assertFalse(target.exists())
            self.assertNotIn("person@example.test", output + error)

    def test_demo_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "child" / ".." / "demo"
            code, _, error = self.call(["demo", "--output-dir", str(target)])
            self.assertEqual(code, 4)
            self.assertIn("E_UNSAFE_PATH", error)
