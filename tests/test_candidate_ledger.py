from __future__ import annotations

from datetime import datetime, timezone
import json
import unittest
from unittest import mock

from requirement_ledger.candidate_ledger import (
    CURRENT_SCHEMA_VERSION,
    CandidateHeadError,
    CandidateLedgerError,
    CandidateTransitionError,
    STATE_SCHEMA_VERSION,
    sync_candidate_state,
    target_sha256,
    validate_candidate_input,
    validate_candidate_state,
)


NOW = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)


def entry(candidate_id: str = "c1", status: str = "candidate", **overrides: object) -> dict:
    value = {
        "id": candidate_id,
        "status": status,
        "title": "Keep explicit scope",
        "evidence_refs": ["report-17"],
        "preserve": "Explicit selection remains required.",
        "smallest_change": "Add a bounded validator.",
        "success": "The validator accepts the intended state.",
        "boundary": "No implementation or external action.",
        "rollback": "Remove the isolated validator.",
        "disproof": "A bounded negative test demonstrates failure.",
    }
    value.update(overrides)
    return value


def current(target: str, entries: list[dict], expected_head: str = "none") -> dict:
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "target_sha256": target_sha256(target),
        "expected_head": expected_head,
        "entries": entries,
    }


class CandidateLedgerTests(unittest.TestCase):
    def test_first_run_is_hashed_sorted_and_private(self) -> None:
        state = sync_candidate_state(
            "task-42", current("task-42", [entry("z9"), entry("a1")]), generated_at=NOW
        )
        self.assertEqual(state["schema_version"], STATE_SCHEMA_VERSION)
        self.assertEqual([item["id"] for item in state["entries"]], ["a1", "z9"])
        self.assertTrue(all(item["carried"] is False for item in state["entries"]))
        self.assertNotIn("target", state)
        self.assertNotIn("task-42", repr(state))

    def test_legal_transition_and_timestamp_bound_deterministic_head(self) -> None:
        first = sync_candidate_state("task", current("task", [entry()]), generated_at=NOW)
        next_current = current("task", [entry(status="authorised")], first["head"])
        second = sync_candidate_state("task", next_current, first, generated_at=NOW)
        later = sync_candidate_state(
            "task", next_current, first, generated_at=datetime(2026, 8, 31, tzinfo=timezone.utc)
        )
        repeat = sync_candidate_state("task", next_current, first, generated_at=NOW)
        self.assertEqual(second["entries"][0]["status"], "authorised")
        self.assertEqual(second["head"], repeat["head"])
        self.assertNotEqual(second["generated_at"], later["generated_at"])
        self.assertNotEqual(second["head"], later["head"])

    def test_illegal_transition_is_rejected(self) -> None:
        first = sync_candidate_state("task", current("task", [entry()]), generated_at=NOW)
        with self.assertRaises(CandidateTransitionError):
            sync_candidate_state(
                "task", current("task", [entry(status="validated")], first["head"]), first, NOW
            )

    def test_stale_head_and_cross_target_are_rejected(self) -> None:
        first = sync_candidate_state("task", current("task", [entry()]), generated_at=NOW)
        with self.assertRaises(CandidateHeadError):
            sync_candidate_state("task", current("task", [entry()], "0" * 64), first, NOW)
        with self.assertRaises(CandidateLedgerError):
            sync_candidate_state("other", current("task", [entry()]), generated_at=NOW)
        with self.assertRaises(CandidateLedgerError):
            sync_candidate_state("other", current("other", [entry()], first["head"]), first, NOW)

    def test_duplicate_ids_fail_and_candidate_is_carried(self) -> None:
        with self.assertRaises(CandidateLedgerError):
            validate_candidate_input(current("task", [entry(), entry()]))
        first = sync_candidate_state("task", current("task", [entry("keep")]), generated_at=NOW)
        carried = sync_candidate_state("task", current("task", [], first["head"]), first, NOW)
        self.assertEqual(carried["entries"][0]["id"], "keep")
        self.assertTrue(carried["entries"][0]["carried"])

    def test_all_unresolved_states_carry_and_resolved_states_do_not(self) -> None:
        first = sync_candidate_state("task", current("task", [entry()]), generated_at=NOW)
        authorised = sync_candidate_state(
            "task", current("task", [entry(status="authorised")], first["head"]), first, NOW
        )
        absent = sync_candidate_state("task", current("task", [], authorised["head"]), authorised, NOW)
        self.assertEqual(absent["entries"][0]["status"], "authorised")
        self.assertTrue(absent["entries"][0]["carried"])

        implemented = sync_candidate_state(
            "task",
            current("task", [entry(status="implemented-unverified")], authorised["head"]),
            authorised,
            NOW,
        )
        validated = sync_candidate_state(
            "task",
            current("task", [entry(status="validated")], implemented["head"]),
            implemented,
            NOW,
        )
        removed = sync_candidate_state(
            "task", current("task", [], validated["head"]), validated, NOW
        )
        self.assertEqual(removed["entries"], [])

    def test_frozen_transition_table_is_exhaustive(self) -> None:
        allowed = {
            "candidate": {"candidate", "authorised"},
            "authorised": {"authorised", "implemented-unverified"},
            "implemented-unverified": {
                "implemented-unverified", "validated", "regressed", "rolled-back",
            },
            "validated": {"validated", "regressed"},
            "regressed": {"regressed", "implemented-unverified", "rolled-back"},
            "rolled-back": {"rolled-back"},
        }
        for old_status, new_statuses in allowed.items():
            with self.subTest(old_status=old_status):
                seed = sync_candidate_state("task", current("task", [entry()]), generated_at=NOW)
                state = seed
                if old_status != "candidate":
                    route = {
                        "authorised": ["authorised"],
                        "implemented-unverified": ["authorised", "implemented-unverified"],
                        "validated": ["authorised", "implemented-unverified", "validated"],
                        "regressed": ["authorised", "implemented-unverified", "regressed"],
                        "rolled-back": ["authorised", "implemented-unverified", "rolled-back"],
                    }[old_status]
                    for status in route:
                        state = sync_candidate_state(
                            "task", current("task", [entry(status=status)], state["head"]), state, NOW
                        )
                for new_status in allowed:
                    action = lambda: sync_candidate_state(
                        "task",
                        current("task", [entry(status=new_status)], state["head"]),
                        state,
                        NOW,
                    )
                    if new_status in new_statuses:
                        action()
                    else:
                        with self.assertRaises(CandidateTransitionError):
                            action()

    def test_malformed_unknown_and_limit_values_fail_closed(self) -> None:
        bad = current("task", [entry(candidate_id="bad/id")])
        with self.assertRaises(CandidateLedgerError):
            validate_candidate_input(bad)
        unknown = current("task", [entry()])
        unknown["unexpected"] = "no"
        with self.assertRaises(CandidateLedgerError):
            validate_candidate_input(unknown)
        controls = current("task", [entry(title="line one\nline two")])
        with self.assertRaises(CandidateLedgerError):
            validate_candidate_input(controls)
        too_long = current("task", [entry(title="x" * 513)])
        with self.assertRaises(CandidateLedgerError):
            validate_candidate_input(too_long)
        too_many_refs = current("task", [entry(evidence_refs=[f"r{index}" for index in range(33)])])
        with self.assertRaises(CandidateLedgerError):
            validate_candidate_input(too_many_refs)
        too_many = current("task", [entry(f"c{index}") for index in range(257)])
        with self.assertRaises(CandidateLedgerError):
            validate_candidate_input(too_many)

    def test_tampered_state_is_rejected(self) -> None:
        state = sync_candidate_state("task", current("task", [entry()]), generated_at=NOW)
        state["entries"][0]["title"] = "Different"
        with self.assertRaises(CandidateHeadError):
            validate_candidate_state(state)
        state = sync_candidate_state("task", current("task", [entry()]), generated_at=NOW)
        state["generated_at"] = "2099-01-01T00:00:00.000000Z"
        with self.assertRaises(CandidateHeadError):
            validate_candidate_state(state)
        state = sync_candidate_state("task", current("task", [entry()]), generated_at=NOW)
        state["unknown"] = True
        with self.assertRaises(CandidateLedgerError):
            validate_candidate_state(state)

    def test_persisted_utf8_state_must_fit_the_cli_roundtrip_limit(self) -> None:
        rich = entry(
            title="😀" * 128,
            preserve="界" * 256,
            smallest_change="修" * 256,
        )
        state = sync_candidate_state("task", current("task", [rich]), generated_at=NOW)
        persisted_size = len(
            (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
        with mock.patch(
            "requirement_ledger.candidate_ledger.MAX_CANDIDATE_STATE_BYTES",
            persisted_size,
        ):
            self.assertEqual(validate_candidate_state(state)["head"], state["head"])
        with mock.patch(
            "requirement_ledger.candidate_ledger.MAX_CANDIDATE_STATE_BYTES",
            persisted_size - 1,
        ):
            with self.assertRaises(CandidateLedgerError):
                validate_candidate_state(state)


if __name__ == "__main__":
    unittest.main()
