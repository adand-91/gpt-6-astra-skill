#!/usr/bin/env python3
"""Tests for the mechanical layer.

The fixtures below encode the traps found in real transcripts.  Each one cost a wrong
number before it was understood, so each one has a test.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from scan_transcript import (  # noqa: E402
    MAX_LINE_BYTES,
    aggregate,
    command_shape,
    is_correction,
    matches_project,
    ngrams,
    parse_claude,
    parse_codex,
    parse_text,
    parse_when,
    too_old,
)


def write_lines(path: Path, rows: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                    encoding="utf-8")
    return path


def claude_user(text: str, **extra) -> dict:
    row = {"type": "user", "timestamp": "2026-08-17T10:00:00Z", "cwd": "/work/proj",
           "message": {"role": "user", "content": [{"type": "text", "text": text}]}}
    row.update(extra)
    return row


def claude_tool_result(tool_use_id: str, text: str, is_error: bool = False) -> dict:
    """The trap: Claude Code feeds tool output back as a *user* line."""
    return {"type": "user", "timestamp": "2026-08-17T10:00:01Z",
            "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tool_use_id,
                 "content": text, "is_error": is_error}]}}


def claude_assistant(tool: str | None = None, command: str | None = None) -> dict:
    blocks: list[dict] = [{"type": "thinking", "thinking": "..."}]
    if tool:
        blocks.append({"type": "tool_use", "id": "t1", "name": tool,
                       "input": {"command": command} if command else {}})
    else:
        blocks.append({"type": "text", "text": "done"})
    return {"type": "assistant", "timestamp": "2026-08-17T10:00:02Z",
            "message": {"role": "assistant", "content": blocks}}


class TestClaude(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def parse(self, rows: list[dict]):
        return parse_claude(write_lines(self.dir / "s.jsonl", rows))

    def test_tool_results_are_not_user_turns(self) -> None:
        facts = self.parse([
            claude_user("do the thing"),
            claude_assistant(tool="Bash", command="ls /tmp"),
            claude_tool_result("t1", "a\nb\nc"),
            claude_tool_result("t1", "d"),
        ])
        self.assertEqual(facts["counts"]["user_turns"], 1)

    def test_tool_error_is_attributed_to_its_tool(self) -> None:
        facts = self.parse([
            claude_user("go"),
            claude_assistant(tool="Bash", command="false"),
            claude_tool_result("t1", "command failed", is_error=True),
        ])
        self.assertEqual(facts["counts"]["tool_errors"], 1)
        self.assertEqual(facts["errors"][0]["tool"], "Bash")

    def test_sidechain_turns_are_counted_but_excluded(self) -> None:
        facts = self.parse([
            claude_user("main"),
            claude_user("sub", isSidechain=True),
        ])
        self.assertEqual(facts["counts"]["user_turns"], 1)
        self.assertEqual(facts["counts"]["sidechain_turns"], 1)

    def test_meta_lines_are_ignored(self) -> None:
        facts = self.parse([claude_user("real"), claude_user("meta", isMeta=True)])
        self.assertEqual(facts["counts"]["user_turns"], 1)

    def test_oversized_line_is_measured_not_parsed(self) -> None:
        path = self.dir / "big.jsonl"
        huge = {"type": "user", "message": {"role": "user", "content": [
            {"type": "image", "source": {"data": "A" * (MAX_LINE_BYTES + 10)}}]}}
        write_lines(path, [claude_user("hi"), huge])
        facts = parse_claude(path)
        self.assertEqual(facts["counts"]["oversized_lines"], 1)
        self.assertEqual(facts["counts"]["user_turns"], 1)

    def test_unparsable_line_is_counted(self) -> None:
        path = self.dir / "bad.jsonl"
        path.write_text(json.dumps(claude_user("ok")) + "\nnot json\n", encoding="utf-8")
        facts = parse_claude(path)
        self.assertEqual(facts["counts"]["unparsable_lines"], 1)

    def test_cwd_and_times_are_recorded(self) -> None:
        facts = self.parse([claude_user("hi")])
        self.assertEqual(facts["cwd"], "/work/proj")
        self.assertTrue(facts["first_seen"].startswith("2026-08-17T10:00:00"))

    def test_string_content_user_line_counts(self) -> None:
        facts = self.parse([{"type": "user", "timestamp": "2026-08-17T10:00:00Z",
                             "message": {"role": "user", "content": "plain string"}}])
        self.assertEqual(facts["counts"]["user_turns"], 1)


class TestCodex(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def parse(self, rows: list[dict]):
        return parse_codex(write_lines(self.dir / "rollout-x.jsonl", rows))

    def test_event_user_message_is_the_real_input(self) -> None:
        facts = self.parse([
            {"type": "event_msg", "timestamp": "2026-08-17T10:00:00Z",
             "payload": {"type": "user_message", "message": "build it"}},
            {"type": "response_item", "timestamp": "2026-08-17T10:00:00Z",
             "payload": {"type": "message", "role": "user",
                         "content": [{"text": "injected context blob"}]}},
        ])
        self.assertEqual(facts["counts"]["user_turns"], 1)
        self.assertEqual(facts["user_messages"][0]["text"], "build it")

    def test_response_item_user_is_the_fallback(self) -> None:
        facts = self.parse([
            {"type": "response_item", "timestamp": "2026-08-17T10:00:00Z",
             "payload": {"type": "message", "role": "user",
                         "content": [{"text": "only record of the ask"}]}},
        ])
        self.assertEqual(facts["counts"]["user_turns"], 1)

    def test_tool_calls_and_failed_output(self) -> None:
        facts = self.parse([
            {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec",
                                                  "call_id": "c1",
                                                  "input": {"command": "pytest -q"}}},
            {"type": "response_item", "payload": {"type": "custom_tool_call_output",
                                                  "call_id": "c1",
                                                  "output": "Traceback (most recent call last)"}},
        ])
        self.assertEqual(facts["counts"]["tool_calls"], 1)
        self.assertEqual(facts["counts"]["tool_errors"], 1)
        self.assertEqual(facts["errors"][0]["tool"], "exec")

    def test_failed_patch_is_an_error(self) -> None:
        facts = self.parse([{"type": "event_msg", "payload": {
            "type": "patch_apply_end", "success": False, "stderr": "no such file"}}])
        self.assertEqual(facts["counts"]["tool_errors"], 1)

    def test_compaction_is_counted(self) -> None:
        facts = self.parse([{"type": "compacted", "payload": {"type": "compacted"}}])
        self.assertEqual(facts["counts"]["compactions"], 1)


class TestText(unittest.TestCase):
    def test_plain_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.md"
            path.write_text("## user\nmake a chart\n\n## assistant\nhere\n\n"
                            "## 用户\n不对 换成柱状图\n", encoding="utf-8")
            facts = parse_text(path)
            self.assertEqual(facts["counts"]["user_turns"], 2)
            self.assertEqual(facts["counts"]["assistant_turns"], 1)
            self.assertEqual(len(facts["corrections"]), 1)


class TestSignals(unittest.TestCase):
    def test_corrections_in_both_languages(self) -> None:
        for text in ("不对 我说的是另一个", "错了 重新做", "that's not what I meant",
                     "no, revert that", "先停一下"):
            self.assertTrue(is_correction(text), text)

    def test_ordinary_text_is_not_a_correction(self) -> None:
        for text in ("看起来不错", "go ahead and ship it", "把图放大一点"):
            self.assertFalse(is_correction(text), text)

    def test_command_shape_collapses_paths_and_numbers(self) -> None:
        a = command_shape("python3 /a/b/gen.py --out /tmp/x1 --seed 7")
        b = command_shape("python3 /c/d/gen.py --out /tmp/x2 --seed 99")
        self.assertEqual(a, b)

    def test_command_shape_keeps_different_commands_apart(self) -> None:
        self.assertNotEqual(command_shape("pytest -q"), command_shape("ruff check ."))

    def test_ngrams(self) -> None:
        self.assertEqual(list(ngrams(["a", "b", "c", "d"], 3)),
                         [("a", "b", "c"), ("b", "c", "d")])

    def test_aggregate_surfaces_repeats_over_threshold(self) -> None:
        base = {"counts": {}, "errors": [], "user_messages": [], "corrections": [],
                "bytes": 0, "tool_sequence": ["Read", "Write", "Bash"] * 3}
        from collections import Counter
        session = dict(base, tools=Counter({"Bash": 3}),
                       command_shapes=Counter({"python x.py": 4, "once": 1}))
        agg = aggregate([session])
        shapes = {c["shape"]: c["times"] for c in agg["repeated_commands"]}
        self.assertEqual(shapes.get("python x.py"), 4)
        self.assertNotIn("once", shapes)


class TestFilters(unittest.TestCase):
    def test_parse_when_relative_and_iso(self) -> None:
        self.assertIsNotNone(parse_when("7d"))
        self.assertIsNotNone(parse_when("36h"))
        self.assertEqual(parse_when("2026-08-17T00:00:00Z").year, 2026)
        self.assertIsNone(parse_when(None))

    def test_parse_when_rejects_nonsense(self) -> None:
        with self.assertRaises(SystemExit):
            parse_when("last tuesday")

    def test_project_matches_by_cwd_when_path_is_slugified(self) -> None:
        # The real case: Claude Code turns 接单工作台 into dashes in the directory name.
        path = Path("/Users/x/.claude/projects/-Users-x-Desktop------/s.jsonl")
        facts = {"cwd": "/Users/x/Desktop/接单工作台"}
        self.assertTrue(matches_project(path, facts, "接单工作台"))
        self.assertFalse(matches_project(path, facts, "轻小说"))

    def test_project_matches_by_path_too(self) -> None:
        path = Path("/Users/x/.claude/projects/-Users-x-Desktop-WQ----/s.jsonl")
        self.assertTrue(matches_project(path, {"cwd": None}, "WQ"))

    def test_no_project_filter_matches_everything(self) -> None:
        self.assertTrue(matches_project(Path("/any"), {}, None))

    def test_too_old_skips_stale_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "old.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            old = time.time() - 60 * 60 * 24 * 30
            os.utime(path, (old, old))
            self.assertTrue(too_old(path, datetime.now(timezone.utc) - timedelta(days=7)))
            self.assertFalse(too_old(path, None))

    def test_fresh_file_is_not_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "new.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            self.assertFalse(too_old(path, datetime.now(timezone.utc) - timedelta(days=7)))


if __name__ == "__main__":
    unittest.main()
