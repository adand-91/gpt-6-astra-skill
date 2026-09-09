from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import unittest

from requirement_ledger.candidate_ledger import CURRENT_SCHEMA_VERSION, sync_candidate_state, target_sha256
from requirement_ledger.cli import main as cli_main
from requirement_ledger.review import build_daily_scaffold
from requirement_ledger.review_pack import build_source_pack


NOW = datetime(2026, 8, 30, 8, 1, tzinfo=timezone.utc)


def entry() -> dict:
    return {
        "id": "cand_handoff_01",
        "status": "candidate",
        "title": "Bind the final report",
        "evidence_refs": ["src_handoff_01"],
        "preserve": "Keep exact source selection.",
        "smallest_change": "Bind the reviewed bytes.",
        "success": "The unchanged handoff passes.",
        "boundary": "A one-byte change fails.",
        "rollback": "Discard the binding file.",
        "disproof": "A changed report still passes.",
    }


class RC1CLITests(unittest.TestCase):
    def call(self, argv: list[str]) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = cli_main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def make_case(self, root: Path, *, completeness: str = "complete") -> dict[str, Path]:
        target = "handoff-task"
        source = root / "source.txt"
        source.write_text("bounded evidence\n", encoding="utf-8")
        pack_path = root / "sources.private.json"
        pack_path.write_text(
            json.dumps(build_source_pack(target, root, [source], NOW)), encoding="utf-8"
        )
        current = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "target_sha256": target_sha256(target),
            "expected_head": "none",
            "entries": [entry()],
        }
        state_path = root / "state.private.json"
        state_path.write_text(
            json.dumps(sync_candidate_state(target, current, generated_at=NOW)), encoding="utf-8"
        )
        report_path = root / "review.md"
        report = build_daily_scaffold(
            target,
            "Etc/UTC",
            start="2026-08-29T08:00:00+00:00",
            end="2026-08-30T08:00:00+00:00",
            generated_at=NOW,
        )
        report = report.replace("status: draft", "status: final", 1)
        report = report.replace("source_count: 0", "source_count: 1", 1)
        report = report.replace("completeness: incomplete", f"completeness: {completeness}", 1)
        report = report.replace(
            "- No outcome verified yet: UNKNOWN",
            "- SAID: One explicit source was reviewed.",
            1,
        )
        report_path.write_text(report, encoding="utf-8")
        return {
            "source": source,
            "pack": pack_path,
            "state": state_path,
            "report": report_path,
            "binding": root / "binding.private.json",
        }

    def bind_command(self, root: Path, case: dict[str, Path]) -> list[str]:
        return [
            "review-bind", "--target", "handoff-task", "--scope-root", str(root),
            "--report", str(case["report"]), "--source-pack", str(case["pack"]),
            "--source", str(case["source"]), "--candidate-state", str(case["state"]),
            "--output", str(case["binding"]),
        ]

    def check_command(self, root: Path, case: dict[str, Path]) -> list[str]:
        return [
            "review-handoff-check", "--binding", str(case["binding"]),
            "--target", "handoff-task", "--scope-root", str(root),
            "--report", str(case["report"]), "--source-pack", str(case["pack"]),
            "--source", str(case["source"]), "--candidate-state", str(case["state"]),
        ]

    def test_bind_and_handoff_are_private_read_only_and_fail_on_report_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = self.make_case(root)
            code, output, error = self.call(self.bind_command(root, case))
            self.assertEqual(code, 0, error)
            self.assertIn("WROTE_PRIVATE_REVIEW_BINDING", output)
            self.assertIn("authority_granted=no", output)
            value = json.loads(case["binding"].read_text(encoding="utf-8"))
            self.assertFalse(value["authority_granted"])
            self.assertNotIn("handoff-task", repr(value))
            self.assertNotIn(str(case["report"]), repr(value))
            if os.name != "nt":
                self.assertEqual(case["binding"].stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.call(self.bind_command(root, case))[0], 4)

            before = set(root.iterdir())
            code, output, error = self.call(self.check_command(root, case))
            self.assertEqual(code, 0, error)
            self.assertIn("REVIEW_HANDOFF_IDENTITY_READY", output)
            self.assertIn("execution=no", output)
            self.assertEqual(before, set(root.iterdir()))

            case["report"].write_text(
                case["report"].read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            code, _, error = self.call(self.check_command(root, case))
            self.assertEqual(code, 6)
            self.assertIn("E_REVIEW_BINDING_VERIFY", error)

    def test_incomplete_binding_is_archivable_but_not_handoff_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = self.make_case(root, completeness="incomplete")
            code, _, error = self.call(self.bind_command(root, case))
            self.assertEqual(code, 0, error)
            check = self.check_command(root, case)
            code, _, error = self.call(check)
            self.assertEqual(code, 7)
            self.assertIn("E_INCOMPLETE_EVIDENCE", error)
            code, output, error = self.call(check + ["--allow-incomplete-archive"])
            self.assertEqual(code, 0, error)
            self.assertIn("REVIEW_ARCHIVE_IDENTITY_VERIFIED", output)
            self.assertIn("authority_granted=no", output)


if __name__ == "__main__":
    unittest.main()
