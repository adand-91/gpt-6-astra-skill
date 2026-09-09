from __future__ import annotations

import inspect
import os
import tempfile
import unittest
import ctypes
from pathlib import Path
from unittest import mock

import requirement_ledger._win32safe as win32safe
import requirement_ledger.safeio as safeio
from requirement_ledger._win32safe import (
    UnsupportedPlatformError,
    Win32SafeIOError,
    create_new_directory,
    create_new_file,
    profile_directory,
    validate_leaf_name,
)


class WindowsLeafContractTests(unittest.TestCase):
    def test_accepts_one_unicode_leaf(self) -> None:
        self.assertEqual(validate_leaf_name("审核-β.private.json"), "审核-β.private.json")

    def test_rejects_empty_traversal_separators_ads_and_trailing_aliases(self) -> None:
        invalid = (
            "", ".", "..", "../x", "a/b", r"a\b", "stream:data",
            "wild*card", "question?", "quote\"", "pipe|", "less<", "more>",
            "line\nfeed", "trailing.", "trailing ",
        )
        for leaf in invalid:
            with self.subTest(leaf=leaf):
                with self.assertRaises((TypeError, ValueError)):
                    validate_leaf_name(leaf)

    def test_rejects_reserved_devices_with_extensions_and_case_folding(self) -> None:
        invalid = (
            "CON", "con.txt", "PRN.private.json", "aux", "NUL.log", "CLOCK$",
            "COM1", "com9.txt", "COM¹.txt", "LPT1", "lpt².out", "LPT³",
        )
        for leaf in invalid:
            with self.subTest(leaf=leaf):
                with self.assertRaises(ValueError):
                    validate_leaf_name(leaf)

    def test_rejects_non_string_unpaired_surrogate_and_long_utf16_name(self) -> None:
        for leaf in (None, 1, b"file"):
            with self.subTest(leaf=leaf):
                with self.assertRaises(TypeError):
                    validate_leaf_name(leaf)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            validate_leaf_name("\ud800")
        with self.assertRaises(ValueError):
            validate_leaf_name("\U0001F642" * 128)  # 256 UTF-16 code units.

    def test_rollback_and_profile_contracts_never_use_paths_or_environment(self) -> None:
        source = inspect.getsource(win32safe)
        for forbidden in ("os.unlink", "os.remove", "os.rmdir", ".unlink(", ".rmdir("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        profile_source = inspect.getsource(profile_directory)
        self.assertNotIn("os.environ", profile_source)
        self.assertNotIn("os.getenv", profile_source)
        self.assertNotIn("expanduser(", profile_source)

    def test_native_file_sequence_is_delete_pending_write_flush_commit(self) -> None:
        source = inspect.getsource(create_new_file)
        positions = [
            source.index("_set_delete_pending(child_handle, True)"),
            source.index("_write_all(child_handle, data)"),
            source.index("_verify_path_parent_identity(parent_path, expected_parent_identity)"),
            source.index("_set_delete_pending(child_handle, False)"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_disposition_abi_and_pre_return_rollback_are_explicit(self) -> None:
        source = inspect.getsource(win32safe)
        self.assertIn('_fields_ = [("DeleteFile", ctypes.c_ubyte)]', source)
        self.assertIn('ctypes.sizeof(_FILE_DISPOSITION_INFO) != 1', source)
        relative_source = inspect.getsource(win32safe._relative_create)
        self.assertLess(
            relative_source.index("if int(io_status.Information) != _FILE_CREATED"),
            relative_source.index("_set_delete_pending(child.value, True)"),
        )
        rollback = relative_source.index("_set_delete_pending(child.value, True)")
        self.assertLess(
            rollback,
            relative_source.index("_close_no_raise(child.value)", rollback),
        )

    def test_public_helpers_reject_malformed_parent_identities_before_dispatch(self) -> None:
        invalid = (None, [1, 2], (1,), (1, 2, 3), (True, 2), (1, False))
        for identity in invalid:
            with self.subTest(identity=identity):
                with self.assertRaises(ValueError):
                    create_new_file(
                        Path("."), "new.txt", b"data", 0o600,
                        expected_parent_identity=identity,  # type: ignore[arg-type]
                    )
                with self.assertRaises(ValueError):
                    create_new_directory(
                        Path("."), "new-dir",
                        expected_parent_identity=identity,  # type: ignore[arg-type]
                    )

    def test_safeio_dispatches_windows_before_any_full_path_fallback(self) -> None:
        write_source = inspect.getsource(safeio.write_new_text)
        directory_source = inspect.getsource(safeio.new_output_directory)
        self.assertLess(
            write_source.index('if os.name == "nt"'),
            write_source.index("os.open"),
        )
        self.assertIn("create_new_file", write_source)
        self.assertLess(
            directory_source.index('if os.name == "nt"'),
            directory_source.index("os.mkdir"),
        )
        self.assertIn("create_new_directory", directory_source)
        self.assertIn(
            "expected_parent_identity",
            inspect.signature(create_new_file).parameters,
        )


@unittest.skipIf(os.name == "nt", "non-Windows fail-closed contract")
class NonWindowsContractTests(unittest.TestCase):
    def test_windows_operations_fail_explicitly_but_import_succeeds(self) -> None:
        with self.assertRaises(UnsupportedPlatformError):
            create_new_file(
                Path("."), "new.txt", b"data", 0o600,
                expected_parent_identity=(0, 0),
            )
        with self.assertRaises(UnsupportedPlatformError):
            create_new_directory(
                Path("."), "new-dir", expected_parent_identity=(0, 0)
            )
        with self.assertRaises(UnsupportedPlatformError):
            profile_directory()


@unittest.skipUnless(os.name == "nt", "requires Windows native APIs")
class WindowsNativeIntegrationTests(unittest.TestCase):
    def identity(self, parent: Path) -> tuple[int, int]:
        info = os.lstat(parent)
        return info.st_dev, info.st_ino

    def test_create_file_is_exact_and_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            identity = self.identity(parent)
            output = create_new_file(
                parent, "evidence.private.json", b"{\"ok\":true}\n", 0o600,
                expected_parent_identity=identity,
            )
            self.assertEqual(output, parent / "evidence.private.json")
            self.assertEqual(output.read_bytes(), b"{\"ok\":true}\n")
            with self.assertRaises(Win32SafeIOError):
                create_new_file(
                    parent, output.name, b"replacement", 0o600,
                    expected_parent_identity=identity,
                )
            self.assertEqual(output.read_bytes(), b"{\"ok\":true}\n")

    def test_file_disposition_info_matches_the_native_one_byte_abi(self) -> None:
        self.assertEqual(ctypes.sizeof(win32safe._FILE_DISPOSITION_INFO), 1)

    def test_create_shared_file_and_private_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            identity = self.identity(parent)
            shared = create_new_file(
                parent, "report.md", b"# report\n", 0o644,
                expected_parent_identity=identity,
            )
            directory = create_new_directory(
                parent, "evidence", expected_parent_identity=identity
            )
            self.assertEqual(shared.read_bytes(), b"# report\n")
            self.assertTrue(directory.is_dir())
            with self.assertRaises(Win32SafeIOError):
                create_new_directory(
                    parent, directory.name, expected_parent_identity=identity
                )

    def test_invalid_mode_and_data_fail_before_content_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            with self.assertRaises(ValueError):
                create_new_file(
                    parent, "bad-mode.txt", b"secret", 0o666,
                    expected_parent_identity=self.identity(parent),
                )
            with self.assertRaises(TypeError):
                create_new_file(
                    parent, "bad-data.txt", bytearray(b"secret"), 0o600,
                    expected_parent_identity=self.identity(parent),
                )  # type: ignore[arg-type]
            self.assertFalse((parent / "bad-mode.txt").exists())
            self.assertFalse((parent / "bad-data.txt").exists())

    def test_delete_pending_failure_never_writes_caller_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            output = parent / "mark-failure.txt"
            with mock.patch.object(
                win32safe, "_set_delete_pending",
                side_effect=Win32SafeIOError("injected mark failure"),
            ):
                with self.assertRaises(Win32SafeIOError):
                    create_new_file(
                        parent, output.name, b"secret", 0o600,
                        expected_parent_identity=self.identity(parent),
                    )
            self.assertTrue(output.exists())
            self.assertEqual(output.read_bytes(), b"")

    def test_write_or_final_identity_failure_rolls_back_by_handle(self) -> None:
        cases = (
            ("write-failure.txt", "_write_all"),
            ("identity-failure.txt", "_verify_path_parent_identity"),
        )
        for name, operation in cases:
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as temporary:
                parent = Path(temporary)
                output = parent / name
                with mock.patch.object(
                    win32safe, operation,
                    side_effect=Win32SafeIOError(f"injected {operation}"),
                ):
                    with self.assertRaises(Win32SafeIOError):
                        create_new_file(
                            parent, output.name, b"secret", 0o600,
                            expected_parent_identity=self.identity(parent),
                        )
                self.assertFalse(output.exists())

    def test_profile_directory_comes_from_known_folder_api(self) -> None:
        profile = profile_directory()
        self.assertTrue(profile.is_absolute())
        self.assertTrue(profile.is_dir())
