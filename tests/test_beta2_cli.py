from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import unittest

from requirement_ledger.candidate_ledger import CURRENT_SCHEMA_VERSION, target_sha256
from requirement_ledger.cli import main as cli_main


def candidate_entry() -> dict:
    return {
        "id": "cand_scope_01",
        "status": "candidate",
        "title": "Keep explicit scope",
        "evidence_refs": ["src_case_01"],
        "preserve": "Keep the bounded input contract.",
        "smallest_change": "Add one deterministic check.",
        "success": "The intended input passes.",
        "boundary": "A changed input fails.",
        "rollback": "Remove the isolated change.",
        "disproof": "The boundary case unexpectedly passes.",
    }


class Beta2CLITests(unittest.TestCase):
    def call(self, argv: list[str]) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = cli_main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_candidate_sync_is_private_no_overwrite_and_carries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current.private.json"
            state = root / "state.private.json"
            current.write_text(json.dumps({
                "schema_version": CURRENT_SCHEMA_VERSION,
                "target_sha256": target_sha256("selected-task"),
                "expected_head": "none",
                "entries": [candidate_entry()],
            }), encoding="utf-8")
            command = [
                "candidate-sync", "--target", "selected-task", "--scope-root", str(root),
                "--current", str(current), "--output", str(state),
            ]
            code, output, error = self.call(command)
            self.assertEqual(code, 0, error)
            self.assertIn("WROTE_PRIVATE_CANDIDATE_STATE", output)
            first = json.loads(state.read_text(encoding="utf-8"))
            self.assertNotIn("selected-task", repr(first))
            if os.name != "nt":
                self.assertEqual(state.stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.call(command)[0], 4)

            next_input = root / "next.private.json"
            next_input.write_text(json.dumps({
                "schema_version": CURRENT_SCHEMA_VERSION,
                "target_sha256": target_sha256("selected-task"),
                "expected_head": first["head"],
                "entries": [],
            }), encoding="utf-8")
            next_state = root / "next-state.private.json"
            code, output, error = self.call([
                "candidate-sync", "--target", "selected-task", "--scope-root", str(root),
                "--current", str(next_input), "--previous", str(state),
                "--output", str(next_state),
            ])
            self.assertEqual(code, 0, error)
            self.assertIn("carried=1", output)

    def test_source_pack_and_read_only_verify_detect_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.txt"
            second = root / "second.txt"
            pack = root / "sources.private.json"
            first.write_text("first\n", encoding="utf-8")
            second.write_text("second\n", encoding="utf-8")
            build = [
                "source-pack", "--target", "selected-task", "--scope-root", str(root),
                "--source", str(first), "--source", str(second), "--output", str(pack),
            ]
            code, output, error = self.call(build)
            self.assertEqual(code, 0, error)
            self.assertIn("WROTE_PRIVATE_SOURCE_PACK", output)
            value = json.loads(pack.read_text(encoding="utf-8"))
            self.assertNotIn(str(first), repr(value))
            verify = [
                "source-verify", "--pack", str(pack), "--target", "selected-task",
                "--scope-root", str(root), "--source", str(second), "--source", str(first),
            ]
            code, output, error = self.call(verify)
            self.assertEqual(code, 0, error)
            self.assertIn("meaning=byte-identity-only", output)
            first.write_text("First\n", encoding="utf-8")
            code, _, error = self.call(verify)
            self.assertEqual(code, 6)
            self.assertIn("E_SOURCE_PACK_VERIFY", error)

    def test_control_json_must_stay_inside_scope_and_be_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope = root / "scope"
            scope.mkdir()
            outside = root / "outside.private.json"
            outside.write_text("{}", encoding="utf-8")
            code, _, error = self.call([
                "candidate-sync", "--target", "selected-task", "--scope-root", str(scope),
                "--current", str(outside), "--output", str(scope / "state.private.json"),
            ])
            self.assertEqual(code, 4)
            self.assertIn("E_UNSAFE_PATH", error)
            self.assertFalse((scope / "state.private.json").exists())


if __name__ == "__main__":
    unittest.main()
