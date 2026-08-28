from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import requirement_ledger.transcript as transcript
from requirement_ledger.errors import InputChangedError, UnsafePathError
from requirement_ledger.transcript import MAX_LINE_BYTES, parse_explicit_transcript


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


class TestV01Transcript(unittest.TestCase):
    def test_codex_uses_typed_event_and_filters_per_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rollout-demo.jsonl"
            write_jsonl(path, [
                {"type": "event_msg", "timestamp": "2026-01-01T00:00:00Z",
                 "payload": {"type": "user_message", "message": "old"}},
                {"type": "event_msg", "timestamp": "2026-02-01T00:00:00+00:00",
                 "payload": {"type": "user_message", "message": "not what I meant"}},
                {"type": "response_item", "timestamp": "2026-02-01T00:00:01Z",
                 "payload": {"type": "message", "role": "user",
                             "content": [{"text": "injected duplicate"}]}},
            ])
            parsed = parse_explicit_transcript(
                path, provider="auto", since="2026-01-15T00:00:00Z", until="2026-02-02T00:00:00Z"
            )
            messages = [item for item in parsed["events"] if item["kind"] in ("user_message", "correction")]
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["kind"], "correction")
            self.assertEqual(messages[0]["private_text"], "not what I meant")

    def test_claude_tool_result_is_not_a_user_turn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claude.jsonl"
            write_jsonl(path, [
                {"type": "user", "timestamp": "2026-01-01T00:00:00Z",
                 "message": {"role": "user", "content": [{"type": "text", "text": "build"}]}},
                {"type": "user", "timestamp": "2026-01-01T00:00:01Z",
                 "message": {"role": "user", "content": [{"type": "tool_result", "content": "noise"}]}},
            ])
            parsed = parse_explicit_transcript(path, provider="claude")
            user = [item for item in parsed["events"] if item["kind"] == "user_message"]
            self.assertEqual(len(user), 1)

    def test_invalid_or_oversized_jsonl_marks_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rollout-bad.jsonl"
            path.write_text("not json\n" + "x" * (MAX_LINE_BYTES + 1) + "\n", encoding="utf-8")
            parsed = parse_explicit_transcript(path, provider="codex")
            self.assertEqual(parsed["completeness"], "incomplete")
            self.assertEqual(parsed["stats"]["oversized_lines"], 1)
            self.assertEqual(parsed["stats"]["unparsable_or_unknown_lines"], 1)

    def test_oversized_line_is_drained_before_following_jsonl_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rollout-drain.jsonl"
            path.write_text(
                "x" * 256 + "\n" + json.dumps({
                    "type": "event_msg", "payload": {"type": "user_message", "message": "kept"},
                }) + "\n",
                encoding="utf-8",
            )
            with patch.object(transcript, "MAX_LINE_BYTES", 128):
                parsed = parse_explicit_transcript(path, provider="codex")
            self.assertEqual(parsed["stats"]["oversized_lines"], 1)
            self.assertEqual(parsed["events"][0]["private_text"], "kept")

    def test_plain_text_rejects_time_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "transcript.md"
            path.write_text("# User\nhello\n", encoding="utf-8")
            with self.assertRaises(UnsafePathError):
                parse_explicit_transcript(path, provider="text", since="2026-01-01T00:00:00Z")

    def test_codex_fallback_respects_event_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rollout-fallback.jsonl"
            write_jsonl(path, [
                {"type": "response_item", "payload": {
                    "type": "message", "role": "user", "content": [{"text": f"turn {number}"}],
                }}
                for number in range(4)
            ])
            with patch.object(transcript, "MAX_EVENTS_PER_INPUT", 2):
                parsed = parse_explicit_transcript(path, provider="codex")
            self.assertEqual(len(parsed["events"]), 2)
            self.assertEqual(parsed["stats"]["dropped_events"], 2)
            self.assertEqual(parsed["completeness"], "incomplete")

    def test_tool_correlation_maps_respect_event_budget(self) -> None:
        cases = {
            "claude": lambda number: {
                "type": "assistant", "message": {"role": "assistant", "content": [{
                    "type": "tool_use", "id": f"call-{number}", "name": "read_file",
                }]},
            },
            "codex": lambda number: {
                "type": "response_item", "payload": {
                    "type": "function_call", "call_id": f"call-{number}", "name": "read_file",
                },
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for provider, make_row in cases.items():
                path = directory / f"{provider}.jsonl"
                write_jsonl(path, [make_row(number) for number in range(3)])
                with patch.object(transcript, "MAX_EVENTS_PER_INPUT", 2):
                    parsed = parse_explicit_transcript(path, provider=provider)
                self.assertEqual(parsed["stats"]["dropped_tool_mappings"], 1)
                self.assertEqual(parsed["completeness"], "incomplete")

    def test_plain_text_turn_buffer_is_bounded_and_marks_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "transcript.md"
            path.write_text("# User\nthis text is longer than the test budget\n", encoding="utf-8")
            with patch.object(transcript, "MAX_PRIVATE_TEXT", 12):
                parsed = parse_explicit_transcript(path, provider="text")
            event = parsed["events"][0]
            self.assertEqual(event["private_text"], "this text is")
            self.assertTrue(event["metadata"]["private_text_truncated"])
            self.assertEqual(parsed["stats"]["truncated_event_fields"], 1)
            self.assertEqual(parsed["completeness"], "incomplete")

    def test_hash_and_parse_snapshot_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "transcript.md"
            path.write_text("# User\nhello\n", encoding="utf-8")
            stable = (1, 2, 3, 1, 13, 4, 5)
            changed = (1, 2, 3, 1, 14, 6, 7)
            with patch.object(transcript, "_transcript_stat_signature",
                              side_effect=[stable, stable, changed]):
                with self.assertRaises(InputChangedError):
                    parse_explicit_transcript(path, provider="text")

    def test_path_and_handle_metadata_use_identity_plus_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "transcript.md"
            path.write_text("# User\nhello\n", encoding="utf-8")
            real_lstat = transcript.os.lstat

            def lstat_with_different_mode(value: object):
                info = real_lstat(value)
                return SimpleNamespace(
                    st_mode=info.st_mode ^ stat.S_IWGRP,
                    st_nlink=info.st_nlink,
                    st_size=info.st_size,
                    st_mtime_ns=info.st_mtime_ns,
                    st_dev=info.st_dev,
                    st_ino=info.st_ino,
                )

            with patch.object(transcript.os, "lstat", side_effect=lstat_with_different_mode), \
                    patch.object(transcript.os.path, "samestat", return_value=True):
                parsed = parse_explicit_transcript(path, provider="text")
            self.assertEqual(parsed["completeness"], "complete")
