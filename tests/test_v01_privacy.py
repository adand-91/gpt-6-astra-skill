from __future__ import annotations

import tempfile
import os
import unittest
from pathlib import Path
from unittest import mock

from requirement_ledger.errors import InputChangedError, PrivacyBlockError, UnsafePathError
from requirement_ledger.privacy import (assert_automated_privacy_check, finding_counts,
                                        manifest_for_private_texts, redact_text)
from requirement_ledger.safeio import (_forbidden_scope_root, explicit_regular_file,
                                       open_scoped_json_object,
                                       open_scoped_regular_input, private_output_path,
                                       write_new_text)


class TestPrivacy(unittest.TestCase):
    def test_canary_categories_do_not_expose_values(self) -> None:
        canary = (
            "Authorization: Bearer abcdefghijklmnopqrstuvwxyz\n"
            "email person@example.test phone 13800138000\n"
            "path /Users/alice/private token ghp_abcdefghijklmnopqrstuvwxyz123456\n"
        )
        findings = finding_counts(canary)
        self.assertIn("authorization", findings)
        self.assertIn("email", findings)
        self.assertIn("phone", findings)
        self.assertIn("unix_home", findings)
        self.assertIn("known_token", findings)
        self.assertNotIn("person@example.test", str(findings))

    def test_redaction_removes_original_values(self) -> None:
        raw = "contact person@example.test in /home/alice/work"
        redacted, findings = redact_text(raw)
        self.assertNotIn("person@example.test", redacted)
        self.assertNotIn("/home/alice", redacted)
        self.assertEqual(findings["email"], 1)
        self.assertEqual(findings["unix_home"], 1)

    def test_share_gate_fails_closed(self) -> None:
        with self.assertRaises(PrivacyBlockError):
            assert_automated_privacy_check({"message": "send to person@example.test"})

    def test_manifest_contains_counts_not_values(self) -> None:
        manifest = manifest_for_private_texts(["person@example.test", "13800138000"])
        rendered = str(manifest)
        self.assertIn("email", rendered)
        self.assertFalse(manifest["manifest_contains_original_values"])
        self.assertNotIn("contains_original_values", manifest)
        self.assertNotIn("person@example.test", rendered)
        self.assertNotIn("13800138000", rendered)


class TestSafeIO(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "POSIX account database test")
    def test_real_account_home_is_forbidden_when_home_environment_is_changed(self) -> None:
        import pwd

        account_home = Path(pwd.getpwuid(os.getuid()).pw_dir)
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"HOME": tmp}):
                self.assertTrue(_forbidden_scope_root(account_home))

    def test_descriptor_bound_input_rejects_in_place_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_bytes(b"before")
            with self.assertRaises(InputChangedError):
                with open_scoped_regular_input(source, root) as bound:
                    self.assertEqual(bound.handle.read(), b"before")
                    source.write_bytes(b"after!")

    def test_scoped_json_lock_is_held_until_caller_finishes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "state.json"
            source.write_text('{"state":"before"}\n', encoding="utf-8")
            with self.assertRaises(InputChangedError):
                with open_scoped_json_object(source, root) as value:
                    self.assertEqual(value["state"], "before")
                    source.write_text('{"state":"after!"}\n', encoding="utf-8")

    def test_private_output_requires_suffix_and_does_not_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(UnsafePathError):
                private_output_path(root / "evidence.json")
            target = private_output_path(root / "evidence.private.json")
            write_new_text(target, "{}\n", private=True)
            if os.name != "nt":
                self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(UnsafePathError):
                private_output_path(target)

    def test_symlink_input_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "real.txt"
            link = root / "link.txt"
            real.write_text("fixture", encoding="utf-8")
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(UnsafePathError):
                explicit_regular_file(link)

    def test_parent_traversal_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "input.txt").write_text("fixture", encoding="utf-8")
            with self.assertRaises(UnsafePathError):
                explicit_regular_file(root / "child" / ".." / "input.txt")

    def test_output_ancestor_symlink_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "real"
            nested = real / "nested"
            link = root / "linked"
            nested.mkdir(parents=True)
            try:
                link.symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(UnsafePathError):
                private_output_path(link / "nested" / "evidence.private.json")

    def test_parent_replacement_before_write_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = root / "parent"
            escape = root / "escape"
            parent.mkdir()
            escape.mkdir()
            target = private_output_path(parent / "evidence.private.json")
            original = root / "parent-original"
            parent.rename(original)
            try:
                parent.symlink_to(escape, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(UnsafePathError):
                write_new_text(target, "{}\n", private=True)
            self.assertFalse((escape / "evidence.private.json").exists())

    def test_missing_output_parent_is_not_created_implicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "missing" / "evidence.private.json"
            with self.assertRaises(UnsafePathError):
                private_output_path(target)
            self.assertFalse(target.parent.exists())
