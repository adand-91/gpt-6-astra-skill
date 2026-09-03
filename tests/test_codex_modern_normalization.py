from __future__ import annotations

import json
import copy
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import requirement_ledger.transcript as transcript
from requirement_ledger.codex_input import build_codex_input_envelope
from requirement_ledger.errors import InputLimitError, SchemaError
from requirement_ledger.transcript import parse_scoped_codex_transcript


START = datetime.fromisoformat("2026-08-30T00:00:00+00:00")
END = datetime.fromisoformat("2026-08-30T01:00:00+00:00")


def row(number: int, payload: dict, kind: str = "event_msg") -> dict:
    return {
        "type": kind,
        "timestamp": f"2026-08-30T00:00:{number:02d}+00:00",
        "ordinal": number,
        "payload": payload,
    }


def write_rows(scope: Path, rows: list[dict]) -> Path:
    source = scope / "rollout.jsonl"
    source.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in rows) + "\n",
        encoding="utf-8",
    )
    return source


def parse(scope: Path, rows: list[dict]) -> dict:
    return parse_scoped_codex_transcript(
        write_rows(scope, rows), scope, since=START, until=END
    )


class TestCodexModernNormalization(unittest.TestCase):
    def test_completed_items_keep_first_order_and_latest_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            parsed = parse(scope, [
                row(1, {"type": "item_completed", "turn_id": "turn-private-1", "item": {
                    "type": "AgentMessage", "id": "assistant-private-1",
                    "content": [{"type": "text", "text": "assistant secret"}],
                }}),
                row(2, {"type": "item_completed", "turn_id": "turn-private-1", "item": {
                    "type": "CommandExecution", "id": "command-private-1",
                    "status": "completed", "command": "do-not-store-this-command",
                }}),
                row(3, {"type": "task_complete", "turn_id": "turn-private-1"}),
                row(4, {"type": "item_completed", "turn_id": "turn-private-1", "item": {
                    "type": "CommandExecution", "id": "command-private-1",
                    "status": "failed", "aggregated_output": "private failure output",
                }}),
                row(5, {"type": "item_completed", "turn_id": "turn-private-1", "item": {
                    "type": "UserMessage", "id": "user-private-1", "content": [
                        {"type": "text", "text": "wrong: improve the selected Skill"},
                        {"type": "skill", "name": "jiedan-jiaolian",
                         "path": "/Users/private/.codex/skills/jiedan-jiaolian/SKILL.md"},
                    ],
                }}),
            ])

            normalized = parsed["normalization"]
            items = normalized["ordered_completed_items"]
            self.assertEqual([item["kind"] for item in items], [
                "AgentMessage", "CommandExecution", "UserMessage",
            ])
            self.assertEqual(items[1]["first_physical_record"], 2)
            self.assertEqual(items[1]["latest_physical_record"], 4)
            self.assertEqual(items[1]["status"], "failed")
            self.assertEqual(items[1]["snapshot_count"], 2)
            self.assertEqual(normalized["snapshot_dedupe"]["duplicate_item_snapshots"], 1)
            self.assertEqual(normalized["ordered_turn_terminals"][0]["first_physical_record"], 3)
            self.assertEqual(parsed["accounting"]["recognized_records"], 5)
            self.assertEqual(parsed["accounting"]["included_events"], 3)
            self.assertEqual(parsed["completeness"], "complete")

            envelope = build_codex_input_envelope(
                parsed,
                target="jiedan-jiaolian",
                task_ref="opaque-skill-review",
                start=START,
                end=END,
                timezone_name="UTC",
                declared_exclusions=[],
                generated_at=START,
            )
            rendered = json.dumps(envelope, ensure_ascii=False)
            for secret in (
                "turn-private-1", "assistant-private-1", "command-private-1",
                "user-private-1", "assistant secret", "do-not-store-this-command",
                "private failure output", "jiedan-jiaolian", "/Users/private",
            ):
                self.assertNotIn(secret, rendered)
            self.assertEqual(envelope["schema"], "codex-input-envelope/v2")
            self.assertEqual(envelope["normalization"]["parser_version"], "2")

    def test_same_item_id_in_different_turns_is_not_deduplicated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            parsed = parse(scope, [
                row(1, {"type": "item_completed", "turn_id": "turn-a", "item": {
                    "type": "Plan", "id": "same-item", "text": "one",
                }}),
                row(2, {"type": "item_completed", "turn_id": "turn-b", "item": {
                    "type": "Plan", "id": "same-item", "text": "two",
                }}),
            ])
            items = parsed["normalization"]["ordered_completed_items"]
            self.assertEqual(len(items), 2)
            self.assertNotEqual(items[0]["id"], items[1]["id"])
            self.assertEqual(
                parsed["normalization"]["snapshot_dedupe"]["duplicate_item_snapshots"], 0
            )

    def test_structured_exclusions_are_exact_and_balanced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            parsed = parse(scope, [
                row(1, {"thread_source": "automation"}, "session_meta"),
                row(2, {"type": "message", "text": "delegation"},
                    "inter_agent_communication"),
                row(3, {"type": "collab_waiting_end"}),
                row(4, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "CollabAgentToolCall", "id": "collab", "status": "completed",
                }}),
                row(5, {"type": "sub_agent_activity"}),
                row(6, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "SubAgentActivity", "id": "subagent",
                }}),
                row(7, {"type": "message", "role": "system", "content": [
                    {"type": "text", "text": "private system message"},
                ]}, "response_item"),
                row(8, {"type": "compacted", "private": "not retained"}, "compacted"),
            ])
            counts = {
                item["code"]: item["records"]
                for item in parsed["normalization"]["semantic_exclusions"]
            }
            self.assertEqual(counts, {
                "OBSERVED_AUTOMATION_METADATA": 1,
                "OBSERVED_DELEGATION_RECORD": 3,
                "OBSERVED_SUBAGENT_RECORD": 2,
                "OBSERVED_SYSTEM_RECORD": 1,
                "OBSERVED_NON_EVIDENCE_METADATA": 1,
            })
            self.assertEqual(parsed["accounting"]["recognized_records"], 8)
            self.assertEqual(parsed["accounting"]["unsupported_records"], 0)
            self.assertEqual(parsed["accounting"]["physical_records"], 8)
            self.assertEqual(parsed["events"], [])
            self.assertEqual(parsed["completeness"], "incomplete")

    def test_official_turn_aliases_and_persistent_metadata_are_recognized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            rows = [
                row(1, {"type": "task_started", "turn_id": "turn-a"}),
                row(2, {"type": "turn_started", "turn_id": "turn-a"}),
                row(3, {"type": "token_count", "info": {"private": 123}}),
                row(4, {"type": "thread_goal_updated", "goal": "private"}),
                row(5, {"type": "thread_rolled_back", "num_turns": 1}),
                row(6, {"type": "turn_aborted", "reason": "private"}),
                row(7, {"type": "thread_settings_applied", "settings": {}}),
                row(8, {"type": "turn_complete", "turn_id": "turn-a"}),
                row(9, {"type": "task_complete", "turn_id": "turn-a"}),
                row(10, {"type": "collab_waiting_begin"}),
                row(11, {"type": "collab_close_end"}),
                row(12, {"type": "collab_resume_begin"}),
            ]
            parsed = parse(scope, rows)

            counts = {
                item["code"]: item["records"]
                for item in parsed["normalization"]["semantic_exclusions"]
            }
            self.assertEqual(counts["OBSERVED_NON_EVIDENCE_METADATA"], 7)
            self.assertEqual(counts["OBSERVED_DELEGATION_RECORD"], 3)
            terminals = parsed["normalization"]["ordered_turn_terminals"]
            self.assertEqual(len(terminals), 1)
            self.assertEqual(terminals[0]["kind"], "task_complete")
            self.assertEqual(terminals[0]["snapshot_count"], 2)
            self.assertEqual(parsed["accounting"]["recognized_records"], len(rows))
            self.assertEqual(parsed["accounting"]["unsupported_records"], 0)
            self.assertEqual(parsed["parser_version"], "2")
            self.assertEqual(parsed["completeness"], "incomplete")

    def test_unstructured_words_do_not_create_completion_or_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            parsed = parse(scope, [
                row(1, {"type": "user_message",
                        "message": "automation and delegation are complete"}),
                row(2, {"type": "function_call_output", "call_id": "x",
                        "output": "everything completed"}, "response_item"),
            ])
            self.assertEqual(parsed["normalization"]["ordered_completed_items"], [])
            self.assertTrue(all(
                item["records"] == 0
                for item in parsed["normalization"]["semantic_exclusions"]
            ))
            self.assertEqual([event["kind"] for event in parsed["events"]], ["user_message"])
            self.assertEqual(parsed["completeness"], "complete")

    def test_control_character_ids_cannot_alias_snapshot_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            parsed = parse(scope, [
                row(1, {"type": "item_completed", "turn_id": "a\0b", "item": {
                    "type": "Plan", "id": "c", "text": "one",
                }}),
                row(2, {"type": "item_completed", "turn_id": "a", "item": {
                    "type": "Plan", "id": "b\0c", "text": "two",
                }}),
            ])
            self.assertEqual(parsed["normalization"]["ordered_completed_items"], [])
            self.assertEqual(parsed["accounting"]["unsupported_records"], 2)
            self.assertEqual(parsed["completeness"], "incomplete")

    def test_user_input_blocks_use_an_exact_fail_closed_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            accepted = parse(scope, [row(1, {
                "type": "item_completed", "turn_id": "turn", "item": {
                    "type": "UserMessage", "id": "user", "content": [
                        {"type": "text", "text": "wrong", "text_elements": []},
                        {"type": "image", "image_url": "data:image/png;base64,private"},
                        {"type": "local_image", "path": "/private/image.png"},
                        {"type": "audio", "audio_url": "data:audio/wav;base64,private"},
                        {"type": "local_audio", "path": "/private/audio.wav"},
                        {"type": "skill", "name": "private", "path": "/private/SKILL.md"},
                        {"type": "mention", "name": "private", "path": "app://private"},
                    ],
                },
            })])
            self.assertEqual(accepted["accounting"]["unsupported_records"], 0)
            self.assertEqual(accepted["events"][0]["private_text"], "wrong")

            rejected = parse(scope, [
                row(1, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "UserMessage", "id": "future", "content": [
                        {"type": "future_user_prose", "text": "wrong hidden requirement"},
                    ],
                }}),
                row(2, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "UserMessage", "id": "malformed", "content": [
                        {"type": "skill", "name": "missing-path"},
                    ],
                }}),
            ])
            self.assertEqual(rejected["normalization"]["ordered_completed_items"], [])
            self.assertEqual(rejected["events"], [])
            self.assertEqual(rejected["accounting"]["unsupported_records"], 2)
            self.assertEqual(rejected["completeness"], "incomplete")

    def test_normalization_schema_rejects_unbalanced_counts_and_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            parsed = parse(scope, [
                row(1, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "Plan", "id": "plan", "text": "private",
                }}),
                row(2, {"type": "task_complete", "turn_id": "turn"}),
            ])
            kwargs = {
                "target": "target", "task_ref": "task", "start": START, "end": END,
                "timezone_name": "UTC", "declared_exclusions": [], "generated_at": START,
            }
            bad_snapshots = copy.deepcopy(parsed)
            bad_snapshots["normalization"]["snapshot_dedupe"][
                "recognized_item_snapshot_records"
            ] = 999
            with self.assertRaises(SchemaError):
                build_codex_input_envelope(bad_snapshots, **kwargs)

            bad_exclusions = copy.deepcopy(parsed)
            bad_exclusions["normalization"]["semantic_exclusions"][0]["records"] = 999
            with self.assertRaises(SchemaError):
                build_codex_input_envelope(bad_exclusions, **kwargs)

            bad_status = copy.deepcopy(parsed)
            bad_status["normalization"]["ordered_completed_items"][0]["status"] = "failed"
            with self.assertRaises(SchemaError):
                build_codex_input_envelope(bad_status, **kwargs)

    def test_physical_record_work_limit_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            with mock.patch.object(transcript, "MAX_CODEX_RECORDS", 1):
                with self.assertRaises(InputLimitError):
                    parse(scope, [
                        row(1, {"type": "user_message", "message": "one"}),
                        row(2, {"type": "user_message", "message": "two"}),
                    ])

    def test_invalid_final_status_is_unsupported_and_budget_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope = Path(tmp) / "scope"
            scope.mkdir()
            rows = [
                row(1, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "CommandExecution", "id": "bad", "status": "in_progress",
                }}),
                row(2, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "Plan", "id": "one", "text": "one",
                }}),
                row(3, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "Plan", "id": "two", "text": "two",
                }}),
                row(4, {"type": "item_completed", "turn_id": "turn", "item": {
                    "type": "Plan", "id": "two", "text": "two again",
                }}),
            ]
            with mock.patch.object(transcript, "MAX_EVENTS_PER_INPUT", 1):
                parsed = parse(scope, rows)
            self.assertEqual(parsed["accounting"]["unsupported_records"], 1)
            self.assertEqual(parsed["accounting"]["recognized_records"], 3)
            self.assertEqual(
                parsed["normalization"]["snapshot_dedupe"][
                    "dropped_item_snapshot_records"
                ], 2
            )
            self.assertEqual(len(parsed["normalization"]["ordered_completed_items"]), 1)
            self.assertEqual(parsed["completeness"], "incomplete")


if __name__ == "__main__":
    unittest.main()
