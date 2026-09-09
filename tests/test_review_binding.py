from __future__ import annotations

import copy
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from requirement_ledger.candidate_ledger import (
    CURRENT_SCHEMA_VERSION,
    sync_candidate_state,
    target_sha256,
)
from requirement_ledger.errors import (IncompleteEvidenceError, InputChangedError,
                                       InputLimitError, UnsafePathError)
from requirement_ledger.review import SECTIONS, build_daily_scaffold
from requirement_ledger.review_pack import build_source_pack

# RC1 implementation target.  Keeping this import direct makes a missing release
# surface a visible test-collection failure rather than silently skipping the gate.
from requirement_ledger.review_pack import (  # noqa: E402
    ReviewBindingError,
    ReviewBindingVerificationError,
    build_review_binding,
    validate_review_binding,
    verify_review_binding,
)


NOW = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
TARGET = "selected-codex-task"


def candidate_entry() -> dict:
    return {
        "id": "c1",
        "status": "candidate",
        "title": "Keep selected scope",
        "evidence_refs": ["review-17"],
        "preserve": "Explicit selection remains required.",
        "smallest_change": "Add the bounded verification.",
        "success": "The verifier accepts the current inputs.",
        "boundary": "No implementation or external action.",
        "rollback": "Remove the isolated binding.",
        "disproof": "A negative test rejects altered evidence.",
    }


def candidate_state(target: str = TARGET) -> dict:
    current = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "target_sha256": target_sha256(target),
        "expected_head": "none",
        "entries": [candidate_entry()],
    }
    return sync_candidate_state(target, current, generated_at=NOW)


class ReviewBindingTests(unittest.TestCase):
    def make_inputs(self, root: Path, *, completeness: str = "complete") -> tuple:
        scope = root / "scope"
        scope.mkdir()
        source = scope / "source.txt"
        source.write_bytes(b"selected source bytes\n")
        source_pack = build_source_pack(TARGET, scope, [source], NOW)
        report = scope / "final.md"
        report.write_text(self.final_report(completeness), encoding="utf-8")
        return scope, source, report, source_pack, candidate_state()

    def final_report(self, completeness: str = "complete") -> str:
        text = build_daily_scaffold(
            TARGET,
            "Asia/Shanghai",
            start="2026-08-28T08:00:00+08:00",
            end="2026-08-29T08:00:00+08:00",
            generated_at=NOW,
        )
        return (text.replace("status: draft", "status: final", 1)
                    .replace("source_count: 0", "source_count: 1", 1)
                    .replace("completeness: incomplete", f"completeness: {completeness}", 1)
                    .replace("- No outcome verified yet: UNKNOWN",
                             "- SAID: One explicit source was reviewed.", 1))

    def build(self, root: Path, *, completeness: str = "complete", generated_at: datetime = NOW):
        scope, source, report, source_pack, state = self.make_inputs(root, completeness=completeness)
        binding = build_review_binding(
            TARGET, scope, report, source_pack, [source], state, generated_at=generated_at
        )
        return binding, scope, source, report, source_pack, state

    def assert_private_binding(self, binding: dict, report: Path, source: Path) -> None:
        self.assertEqual(binding["schema"], "review-binding/v1")
        self.assertFalse(binding["path_stored"])
        self.assertFalse(binding["report_content_stored"])
        self.assertFalse(binding["source_content_stored"])
        self.assertFalse(binding["network_used"])
        self.assertFalse(binding["authority_granted"])
        self.assertNotIn("target", binding)
        self.assertNotIn("report", binding)
        rendered = repr(binding)
        self.assertNotIn(TARGET, rendered)
        self.assertNotIn(str(report), rendered)
        self.assertNotIn(str(source), rendered)
        self.assertNotIn("selected source bytes", rendered)

    def test_complete_binding_is_private_deterministic_and_reverifies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, scope, source, report, source_pack, state = self.build(root)
            self.assert_private_binding(binding, report, source)
            self.assertEqual(binding["target_sha256"], target_sha256(TARGET))
            self.assertEqual(binding["report_bytes"], len(report.read_bytes()))
            self.assertEqual(binding["source_pack_head"], source_pack["head"])
            self.assertEqual(binding["source_count"], 1)
            self.assertEqual(binding["candidate_head"], state["head"])
            self.assertEqual(binding["candidate_count"], 1)
            self.assertEqual(binding["carried_count"], 0)
            validate_review_binding(binding)
            verified = verify_review_binding(
                binding, TARGET, scope, report, source_pack, [source], state
            )
            self.assertEqual(verified["head"], binding["head"])

            repeat = build_review_binding(
                TARGET, scope, report, source_pack, [source], state,
                generated_at=NOW,
            )
            later = build_review_binding(
                TARGET, scope, report, source_pack, [source], state,
                generated_at=NOW + timedelta(days=1),
            )
            self.assertEqual(repeat["head"], binding["head"])
            self.assertNotEqual(later["generated_at"], binding["generated_at"])
            self.assertNotEqual(later["head"], binding["head"])

    def test_all_artifact_timestamps_are_integrity_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binding, scope, source, report, source_pack, state = self.build(Path(tmp))
            changed_at = "2099-01-01T00:00:00.000000Z"
            changed_binding = copy.deepcopy(binding)
            changed_binding["generated_at"] = changed_at
            with self.assertRaises(ReviewBindingError):
                validate_review_binding(changed_binding)
            changed_pack = copy.deepcopy(source_pack)
            changed_pack["generated_at"] = changed_at
            with self.assertRaises((ReviewBindingError, ReviewBindingVerificationError)):
                verify_review_binding(
                    binding, TARGET, scope, report, changed_pack, [source], state
                )
            changed_state = copy.deepcopy(state)
            changed_state["generated_at"] = changed_at
            with self.assertRaises((ReviewBindingError, ReviewBindingVerificationError)):
                verify_review_binding(
                    binding, TARGET, scope, report, source_pack, [source], changed_state
                )

    def test_report_must_be_final_valid_target_bound_and_source_count_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, scope, source, report, source_pack, state = self.build(root)
            for replacement in (
                ("status: final", "status: draft"),
                ("mode: daily", "mode: invalid"),
                (f"target: {TARGET}", "target: another-target"),
                ("source_count: 1", "source_count: 2"),
            ):
                with self.subTest(replacement=replacement):
                    report.write_text(
                        self.final_report().replace(*replacement, 1), encoding="utf-8"
                    )
                    with self.assertRaises(ReviewBindingError):
                        build_review_binding(TARGET, scope, report, source_pack, [source], state, NOW)

    def test_hidden_comment_or_fenced_body_cannot_be_complete_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, scope, source, report, source_pack, state = self.build(root)
            frontmatter, _, _ = self.final_report().partition("---\n\n")
            hidden_contract_words = "\n".join(
                heading[0] for heading in SECTIONS["daily"]
            ) + "\nSAID: hidden\nINFERRED UNKNOWN candidate\n"
            unordered_hidden = "\n  ".join(hidden_contract_words.splitlines())
            ordered_hidden = "\n   ".join(hidden_contract_words.splitlines())
            for body in (
                f"<!--\n{hidden_contract_words}\n-->\n",
                f"```text\n{hidden_contract_words}\n```\n",
                f"- ```text\n  {unordered_hidden}\n  ```\n",
                f"1. ~~~text\n   {ordered_hidden}\n   ~~~\n",
            ):
                with self.subTest(body=body.splitlines()[0]):
                    report.write_text(frontmatter + "---\n\n" + body, encoding="utf-8")
                    with self.assertRaises(ReviewBindingError):
                        build_review_binding(
                            TARGET, scope, report, source_pack, [source], state, NOW
                        )

    def test_reverification_rejects_one_byte_report_source_and_pack_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, scope, source, report, source_pack, state = self.build(root)
            report.write_bytes(report.read_bytes() + b"\n")
            with self.assertRaises(ReviewBindingVerificationError):
                verify_review_binding(binding, TARGET, scope, report, source_pack, [source], state)
            report.write_text(self.final_report(), encoding="utf-8")
            source.write_bytes(b"changed source bytes\n")
            with self.assertRaises(ReviewBindingVerificationError):
                verify_review_binding(binding, TARGET, scope, report, source_pack, [source], state)
            source.write_bytes(b"selected source bytes\n")
            tampered_pack = copy.deepcopy(source_pack)
            tampered_pack["head"] = "0" * 64
            with self.assertRaises((ReviewBindingError, ReviewBindingVerificationError)):
                verify_review_binding(binding, TARGET, scope, report, tampered_pack, [source], state)

    def test_source_drift_during_report_read_never_returns_a_ready_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, scope, source, report, source_pack, state = self.build(root)
            import requirement_ledger.review_pack as review_pack

            original = review_pack._read_bound_report

            def mutate_then_read(target: str, bound_report: object):
                source.write_bytes(b"mutated after source hashing\n")
                return original(target, bound_report)

            with mock.patch.object(review_pack, "_read_bound_report", side_effect=mutate_then_read):
                with self.assertRaises(InputChangedError):
                    build_review_binding(
                        TARGET, scope, report, source_pack, [source], state, NOW
                    )
            source.write_bytes(b"selected source bytes\n")
            with mock.patch.object(review_pack, "_read_bound_report", side_effect=mutate_then_read):
                with self.assertRaises(ReviewBindingVerificationError):
                    verify_review_binding(
                        binding, TARGET, scope, report, source_pack, [source], state
                    )

    def test_candidate_target_head_and_missing_state_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, scope, source, report, source_pack, state = self.build(root)
            altered = copy.deepcopy(state)
            altered["head"] = "0" * 64
            with self.assertRaises((ReviewBindingError, ReviewBindingVerificationError)):
                verify_review_binding(binding, TARGET, scope, report, source_pack, [source], altered)
            other_state = candidate_state("other-target")
            with self.assertRaises((ReviewBindingError, ReviewBindingVerificationError)):
                verify_review_binding(binding, TARGET, scope, report, source_pack, [source], other_state)
            with self.assertRaises(ReviewBindingError):
                build_review_binding(TARGET, scope, report, source_pack, [source], None, NOW)

    def test_validator_rejects_unknown_field_head_and_metadata_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binding, _, _, _, _, _ = self.build(Path(tmp))
            mutations = (
                lambda value: value.update({"unknown": True}),
                lambda value: value.update({"head": "0" * 64}),
                lambda value: value.update({"report_mode": "weekly"}),
                lambda value: value.update({"authority_granted": True}),
                lambda value: value.update({"report_bytes": True}),
            )
            for mutate in mutations:
                with self.subTest(mutate=mutate):
                    value = copy.deepcopy(binding)
                    mutate(value)
                    with self.assertRaises(ReviewBindingError):
                        validate_review_binding(value)

    def test_incomplete_can_be_archived_but_default_handoff_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, scope, source, report, source_pack, state = self.build(
                root, completeness="incomplete"
            )
            with self.assertRaises(IncompleteEvidenceError):
                verify_review_binding(binding, TARGET, scope, report, source_pack, [source], state)
            archived = verify_review_binding(
                binding, TARGET, scope, report, source_pack, [source], state,
                require_complete=False,
            )
            self.assertEqual(archived["head"], binding["head"])
            self.assertFalse(binding["authority_granted"])

    def test_unsafe_report_and_sources_and_report_size_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope, source, report, source_pack, state = self.make_inputs(root)
            report_link = root / "report-link.md"
            try:
                report_link.symlink_to(report)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")
            with self.assertRaises((UnsafePathError, ReviewBindingError)):
                build_review_binding(TARGET, scope, report_link, source_pack, [source], state, NOW)

            source_link = scope / "source-link.txt"
            source_link.symlink_to(source)
            with self.assertRaises((UnsafePathError, ReviewBindingError)):
                build_review_binding(TARGET, scope, report, source_pack, [source_link], state, NOW)
            outside = root / "outside.txt"
            outside.write_bytes(b"outside scope\n")
            with self.assertRaises((UnsafePathError, ReviewBindingError)):
                build_review_binding(TARGET, scope, report, source_pack, [outside], state, NOW)

            import requirement_ledger.review_pack as review_pack
            with mock.patch.object(review_pack, "MAX_REVIEW_BYTES", 16):
                with self.assertRaises(InputLimitError):
                    build_review_binding(TARGET, scope, report, source_pack, [source], state, NOW)

            hard = scope / "source-hard.txt"
            try:
                os.link(source, hard)
            except OSError:
                pass
            else:
                with self.assertRaises((UnsafePathError, ReviewBindingError)):
                    build_review_binding(TARGET, scope, report, source_pack, [hard], state, NOW)


if __name__ == "__main__":
    unittest.main()
