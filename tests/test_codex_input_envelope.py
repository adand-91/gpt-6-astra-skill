from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

import requirement_ledger.safeio as safeio
import requirement_ledger.transcript as transcript
from requirement_ledger.cli import main
from requirement_ledger.codex_input import validate_codex_request
from requirement_ledger.errors import (InputChangedError, InputLimitError,
                                       SchemaError, UnsafePathError)
from requirement_ledger.pipeline import analyze_evidence, build_codex_scan_bundle
from requirement_ledger.review import ReviewInputError
from requirement_ledger.transcript import parse_scoped_codex_transcript


def make_repo(root: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Envelope Tester"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "envelope@example.invalid"], check=True)
    (root / "README.md").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
    return root


def write_jsonl(path: Path, rows: list[object]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


class TestCodexInputEnvelope(unittest.TestCase):
    START = "2026-01-01T00:00:00+00:00"
    END = "2026-01-01T01:00:00+00:00"
    TIMEZONE = "UTC"

    def call(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def make_input(self, root: Path, name: str = "private-codex-export.jsonl") -> Path:
        source = root / name
        rows = [
            {"type": "event_msg", "timestamp": self.START,
             "payload": {"type": "user_message", "message": "wrong canary-original-text@example.test"}},
            {"type": "event_msg", "timestamp": self.END,
             "payload": {"type": "agent_message", "message": "excluded endpoint"}},
            {"type": "event_msg", "timestamp": "not-a-time",
             "payload": {"type": "user_message", "message": "bad timestamp"}},
            {"type": "unknown", "timestamp": "2026-01-01T00:30:00Z", "payload": {}},
        ]
        source.write_text(
            "\n".join(json.dumps(row) for row in rows[:3]) + "\n{not-json}\n" +
            json.dumps(rows[3]) + "\n",
            encoding="utf-8",
        )
        return source

    def build(self, repo: Path, source: Path, scope: Path, **overrides: object) -> dict:
        args: dict[str, object] = {
            "scope_root": scope,
            "target": "requirement-ledger",
            "task_ref": "codex-task-opaque-1",
            "since": self.START,
            "until": self.END,
            "timezone_name": self.TIMEZONE,
            "declared_exclusions": ["system"],
            "deterministic_key": b"codex-envelope-test",
        }
        args.update(overrides)
        return build_codex_scan_bundle(repo, source, **args)  # type: ignore[arg-type]

    def test_single_source_window_accounting_and_envelope_privacy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_repo(root / "repo")
            scope = root / "approved-scope"
            scope.mkdir()
            source = self.make_input(scope)
            bundle = self.build(
                repo,
                source,
                scope,
                target=source.name,
                task_ref="canary-original-text@example.test",
            )

            envelope = bundle["codex_input_envelope"]
            self.assertEqual(envelope["schema"], "codex-input-envelope/v1")
            self.assertEqual(envelope["window"]["semantics"], "[start,end)")
            self.assertEqual(envelope["window"]["start"], self.START)
            self.assertEqual(envelope["window"]["end"], self.END)
            self.assertEqual(envelope["source"]["summary"], {
                "physical_records": 5,
                "recognized_records": 1,
                "included_events": 1,
            })
            exclusions = {item["code"]: item["records"] for item in envelope["exclusions"]}
            self.assertEqual(exclusions["OUTSIDE_HALF_OPEN_WINDOW"], 1)
            self.assertEqual(exclusions["MISSING_OR_INVALID_TIMESTAMP"], 1)
            self.assertEqual(exclusions["MALFORMED_RECORD"], 1)
            self.assertEqual(exclusions["UNSUPPORTED_RECORD"], 1)
            self.assertEqual(exclusions["DECLARED_SYSTEM_NOT_SELECTED"], None)
            self.assertEqual(bundle["completeness"], "incomplete")
            analysis = analyze_evidence(bundle)
            self.assertTrue(analysis["issues"])
            self.assertTrue(all(
                issue["decision_status"] == "blocked" for issue in analysis["issues"]
            ))

            rendered = json.dumps(envelope, ensure_ascii=False)
            self.assertNotIn("canary-original-text@example.test", rendered)
            self.assertNotIn(source.name, rendered)
            self.assertNotIn(str(source), rendered)
            self.assertFalse(envelope["target"]["reference_stored"])
            self.assertFalse(envelope["task"]["reference_stored"])
            self.assertFalse(envelope["source"]["content_retained_in_envelope"])
            self.assertFalse(envelope["source"]["path_stored"])
            self.assertFalse(envelope["privacy"]["contains_original_text"])
            self.assertFalse(envelope["privacy"]["contains_file_name"])
            self.assertFalse(envelope["privacy"]["contains_absolute_paths"])
            self.assertEqual(envelope["coverage"]["captured_bytes_binding"], "complete")
            self.assertEqual(
                envelope["coverage"]["path_identity_check"],
                "metadata-checked-best-effort",
            )
            self.assertEqual(envelope["coverage"]["atomic_source_snapshot"], "unknown")
            self.assertFalse(envelope["network_client_used"])
            self.assertNotIn("network_used", envelope)

    def test_cli_private_mode_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_repo(root / "repo")
            scope = root / "scope"
            scope.mkdir()
            source = self.make_input(scope)
            output = root / "bounded.private.json"
            argv = [
                "codex-scan", "--repo", str(repo), "--input", str(source),
                "--scope-root", str(scope), "--target", "requirement-ledger",
                "--task-ref", "opaque-task", "--since", self.START, "--until", self.END,
                "--timezone", self.TIMEZONE, "--output", str(output),
            ]
            code, _, error = self.call(argv)
            self.assertEqual(code, 0, error)
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            before = output.read_bytes()
            code, _, error = self.call(argv)
            self.assertEqual(code, UnsafePathError.exit_code)
            self.assertIn("E_UNSAFE_PATH", error)
            self.assertEqual(output.read_bytes(), before)

    def test_directory_root_home_and_out_of_scope_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope = root / "scope"
            scope.mkdir()
            source = self.make_input(scope)
            with self.assertRaises(UnsafePathError):
                parse_scoped_codex_transcript(scope, scope, since=self._start(), until=self._end())
            with self.assertRaises(UnsafePathError):
                parse_scoped_codex_transcript(source, Path(source.anchor), since=self._start(), until=self._end())
            with self.assertRaises(UnsafePathError):
                parse_scoped_codex_transcript(source, Path.home(), since=self._start(), until=self._end())
            other = self.make_input(root, "outside.jsonl")
            with self.assertRaises(UnsafePathError):
                parse_scoped_codex_transcript(other, scope, since=self._start(), until=self._end())

    def test_final_and_ancestor_symlink_are_rejected_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope = root / "scope"
            real = scope / "real"
            real.mkdir(parents=True)
            source = self.make_input(real)
            final_link = scope / "final-link.jsonl"
            ancestor_link = scope / "ancestor-link"
            try:
                final_link.symlink_to(source)
                ancestor_link.symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(UnsafePathError):
                parse_scoped_codex_transcript(final_link, scope, since=self._start(), until=self._end())
            with self.assertRaises(UnsafePathError):
                parse_scoped_codex_transcript(ancestor_link / source.name, scope,
                                              since=self._start(), until=self._end())

    def test_hardlinked_input_is_rejected_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope = root / "scope"
            scope.mkdir()
            source = self.make_input(scope)
            linked = scope / "hard-link.jsonl"
            try:
                os.link(source, linked)
            except OSError:
                self.skipTest("hard-link creation is unavailable")
            with self.assertRaises(UnsafePathError):
                parse_scoped_codex_transcript(linked, scope, since=self._start(), until=self._end())

    def test_size_limit_is_fail_closed_without_allocating_large_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope = root / "scope"
            scope.mkdir()
            source = self.make_input(scope)
            with mock.patch.object(transcript, "MAX_CODEX_INPUT_BYTES", 1):
                with self.assertRaises(InputLimitError):
                    parse_scoped_codex_transcript(source, scope, since=self._start(), until=self._end())

    def test_invalid_request_and_window_values_are_rejected(self) -> None:
        for target, task in (("contains/path", "opaque"), ("target", "task/with-path"),
                             ("..", "opaque"), ("target", "file:private")):
            with self.assertRaises(SchemaError):
                validate_codex_request(target, task, [])
        with self.assertRaises(SchemaError):
            validate_codex_request("target", "opaque", ["system", "system"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_repo(root / "repo")
            scope = root / "scope"
            scope.mkdir()
            source = self.make_input(scope)
            for kwargs in (
                {"timezone_name": "Not/A_Timezone"},
                {"since": self.END, "until": self.START},
                {"timezone_name": "Asia/Shanghai"},
            ):
                with self.assertRaises(ReviewInputError):
                    self.build(repo, source, scope, **kwargs)

    def test_source_or_scope_drift_fails_before_cli_output_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_repo(root / "repo")
            scope = root / "scope"
            scope.mkdir()
            source = self.make_input(scope)
            args = [
                "codex-scan", "--repo", str(repo), "--input", str(source),
                "--scope-root", str(scope), "--target", "target", "--task-ref", "opaque",
                "--since", self.START, "--until", self.END, "--timezone", self.TIMEZONE,
            ]
            for label, patcher in (
                ("source", mock.patch.object(
                    transcript, "_transcript_stat_signature", side_effect=[(1, 1), (2, 2)])),
                ("scope", mock.patch.object(safeio, "_same_chain", return_value=False)),
            ):
                output = root / f"{label}.private.json"
                with patcher:
                    code, _, error = self.call([*args, "--output", str(output)])
                self.assertEqual(code, InputChangedError.exit_code)
                self.assertIn("E_INPUT_CHANGED", error)
                self.assertFalse(output.exists())

    def test_v01_scan_stays_compatible_with_the_same_codex_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_repo(root / "repo")
            scope = root / "scope"
            scope.mkdir()
            source = self.make_input(scope)
            output = root / "v01.private.json"
            code, _, error = self.call([
                "scan", "--repo", str(repo), "--input", str(source), "--provider", "codex",
                "--since", self.START, "--until", self.END, "--output", str(output),
            ])
            self.assertEqual(code, 0, error)
            bundle = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(bundle["kind"], "private-evidence")
            self.assertEqual(
                sum(item["kind"] == "assistant_message" for item in bundle["evidence"]),
                1,
                "the frozen v0.1 scan keeps its legacy inclusive --until behaviour",
            )

    def _start(self):
        from datetime import datetime
        return datetime.fromisoformat(self.START)

    def _end(self):
        from datetime import datetime
        return datetime.fromisoformat(self.END)
