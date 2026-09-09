from __future__ import annotations

import copy
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from requirement_ledger.errors import InputLimitError, UnsafePathError
from requirement_ledger.review_pack import (
    SourcePackError,
    SourcePackVerificationError,
    build_source_pack,
    validate_source_pack,
    verify_source_pack,
)
import requirement_ledger.review_pack as review_pack


NOW = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)


class SourcePackTests(unittest.TestCase):
    def make_sources(self, root: Path) -> tuple[Path, Path, Path]:
        scope = root / "scope"
        scope.mkdir()
        first = scope / "one.txt"
        second = scope / "two.txt"
        first.write_bytes(b"first source\n")
        second.write_bytes(b"second source\n")
        return scope, first, second

    def test_pack_is_private_canonical_and_order_independent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope, first, second = self.make_sources(Path(tmp))
            one = build_source_pack("opaque-target", scope, [first, second], NOW)
            two = build_source_pack("opaque-target", scope, [second, first], NOW)
            self.assertEqual(one["head"], two["head"])
            self.assertEqual(one["entries"], two["entries"])
            self.assertEqual(one["source_count"], 2)
            self.assertFalse(one["path_stored"])
            self.assertFalse(one["content_stored"])
            self.assertFalse(one["network_used"])
            rendered = repr(one)
            self.assertNotIn("opaque-target", rendered)
            self.assertNotIn(str(first), rendered)
            self.assertNotIn(first.name, rendered)
            self.assertNotIn("first source", rendered)
            validate_source_pack(one)
            verified = verify_source_pack(one, "opaque-target", scope, [second, first])
            self.assertEqual(verified["head"], one["head"])

    def test_same_content_has_deterministic_occurrences_without_deduplication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope, first, second = self.make_sources(Path(tmp))
            first.write_bytes(b"same bytes")
            second.write_bytes(b"same bytes")
            pack = build_source_pack("target", scope, [second, first], NOW)
            self.assertEqual(pack["source_count"], 2)
            self.assertEqual(len(pack["entries"]), 2)
            self.assertEqual(pack["entries"][0]["sha256"], pack["entries"][1]["sha256"])
            self.assertEqual(
                [entry["source_id"][-3:] for entry in pack["entries"]], ["001", "002"]
            )

    def test_empty_duplicate_scope_escape_links_and_hardlinks_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope, first, _ = self.make_sources(root)
            with self.assertRaises(SourcePackError):
                build_source_pack("target", scope, [], NOW)
            with self.assertRaises(SourcePackError):
                build_source_pack("target", scope, [first, first], NOW)
            outside = root / "outside.txt"
            outside.write_text("outside", encoding="utf-8")
            with self.assertRaises(UnsafePathError):
                build_source_pack("target", scope, [outside], NOW)
            link = scope / "link.txt"
            try:
                link.symlink_to(first)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")
            with self.assertRaises(UnsafePathError):
                build_source_pack("target", scope, [link], NOW)
            hard = scope / "hard.txt"
            try:
                os.link(first, hard)
            except OSError:
                return
            with self.assertRaises(UnsafePathError):
                build_source_pack("target", scope, [hard], NOW)

    def test_single_and_total_limits_are_checked_while_streaming(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope, first, second = self.make_sources(Path(tmp))
            with mock.patch.object(review_pack, "MAX_SOURCE_BYTES", 3):
                with self.assertRaises(InputLimitError):
                    build_source_pack("target", scope, [first], NOW)
            first.write_bytes(b"abc")
            second.write_bytes(b"def")
            with mock.patch.object(review_pack, "MAX_TOTAL_BYTES", 5):
                with self.assertRaises(InputLimitError):
                    build_source_pack("target", scope, [first, second], NOW)

    def test_rebinding_rejects_target_or_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope, first, second = self.make_sources(Path(tmp))
            pack = build_source_pack("target", scope, [first, second], NOW)
            with self.assertRaises(SourcePackVerificationError):
                verify_source_pack(pack, "other-target", scope, [first, second])
            first.write_bytes(b"First source\n")
            with self.assertRaises(SourcePackVerificationError):
                verify_source_pack(pack, "target", scope, [first, second])

    def test_validator_rejects_tampering_unknown_fields_and_boolean_integers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope, first, second = self.make_sources(Path(tmp))
            pack = build_source_pack("target", scope, [first, second], NOW)
            for mutate in (
                lambda value: value.update({"unknown": True}),
                lambda value: value.update({"source_count": value["source_count"] + 1}),
                lambda value: value["entries"][0].update({"bytes": True}),
                lambda value: value["entries"].reverse(),
                lambda value: value.update({"head": "0" * 64}),
                lambda value: value.update({"generated_at": "bad\nvalue"}),
                lambda value: value.update({"generated_at": "2099-01-01T00:00:00.000000Z"}),
            ):
                tampered = copy.deepcopy(pack)
                mutate(tampered)
                with self.assertRaises(SourcePackError):
                    validate_source_pack(tampered)

    def test_generated_at_is_bound_into_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scope, first, second = self.make_sources(Path(tmp))
            first_pack = build_source_pack("target", scope, [first, second], NOW)
            second_pack = build_source_pack("target", scope, [first, second], NOW + timedelta(seconds=1))
            self.assertNotEqual(first_pack["generated_at"], second_pack["generated_at"])
            self.assertNotEqual(first_pack["head"], second_pack["head"])


if __name__ == "__main__":
    unittest.main()
