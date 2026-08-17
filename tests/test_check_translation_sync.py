#!/usr/bin/env python3
"""Tests for the translation-drift checker."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_translation_sync import check, sha256_short, skeleton  # noqa: E402

STAMP = "<!-- translation-of: {source} sha256:{digest} -->"


class TestShippedRepo(unittest.TestCase):
    def test_repo_translations_are_in_sync(self) -> None:
        self.assertEqual(check(ROOT), [])


class TestSkeleton(unittest.TestCase):
    def test_heading_levels_and_fences_are_counted(self) -> None:
        text = "# A\n\ntext\n\n## B\n\n```bash\nls\n```\n\n## C\n"
        self.assertEqual(skeleton(text), ((1, 2, 2), 1))

    def test_headings_inside_fences_are_ignored(self) -> None:
        text = "# A\n\n```\n# not a heading\n```\n"
        self.assertEqual(skeleton(text), ((1,), 1))


class TestDrift(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.source = self.root / "DOC.md"
        self.source.write_text("# Title\n\n## Section\n", encoding="utf-8")
        self.mirror = self.root / "DOC.zh-CN.md"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write_mirror(self, body: str, digest: str | None = None) -> None:
        digest = digest if digest is not None else sha256_short(self.source)
        self.mirror.write_text(
            STAMP.format(source="DOC.md", digest=digest) + "\n\n" + body, encoding="utf-8"
        )

    def test_matching_mirror_passes(self) -> None:
        self.write_mirror("# 标题\n\n## 小节\n")
        self.assertEqual(check(self.root), [])

    def test_stale_stamp_is_reported(self) -> None:
        self.write_mirror("# 标题\n\n## 小节\n", digest="deadbeefdeadbeef")
        findings = check(self.root)
        self.assertTrue(any("STALE" in f for f in findings), findings)

    def test_update_restamps(self) -> None:
        self.write_mirror("# 标题\n\n## 小节\n", digest="deadbeefdeadbeef")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check(self.root, update=True), [])
        self.assertIn(sha256_short(self.source), self.mirror.read_text(encoding="utf-8"))

    def test_heading_drift_is_reported(self) -> None:
        self.write_mirror("# 标题\n")
        findings = check(self.root)
        self.assertTrue(any("heading skeleton" in f for f in findings), findings)

    def test_code_block_drift_is_reported(self) -> None:
        self.source.write_text("# Title\n\n## Section\n\n```bash\nls\n```\n", encoding="utf-8")
        self.write_mirror("# 标题\n\n## 小节\n")
        findings = check(self.root)
        self.assertTrue(any("code blocks" in f for f in findings), findings)

    def test_missing_stamp_is_reported(self) -> None:
        self.mirror.write_text("# 标题\n\n## 小节\n", encoding="utf-8")
        findings = check(self.root)
        self.assertTrue(any("no translation-of stamp" in f for f in findings), findings)

    def test_stamp_naming_a_missing_source_is_reported(self) -> None:
        self.mirror.write_text(
            STAMP.format(source="GONE.md", digest="deadbeefdeadbeef") + "\n\n# 标题\n",
            encoding="utf-8",
        )
        findings = check(self.root)
        self.assertTrue(any("missing source" in f for f in findings), findings)

    def test_untranslated_source_is_reported(self) -> None:
        self.write_mirror("# 标题\n\n## 小节\n")
        (self.root / "OTHER.md").write_text("# Other\n", encoding="utf-8")
        findings = check(self.root)
        self.assertTrue(any("no .zh-CN.md translation" in f for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
