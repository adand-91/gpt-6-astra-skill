from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from requirement_ledger.errors import InputChangedError, PrivacyBlockError, UnsafePathError
from requirement_ledger import pipeline as pipeline_module
from requirement_ledger.git_evidence import bind_repo
from requirement_ledger.pipeline import (analyze_evidence, build_evidence_bundle,
                                         build_fix_proposals, render_markdown_report,
                                         share_report, synthetic_demo_bundle,
                                         validate_outcomes)


def make_repo(root: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Synthetic Tester"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "synthetic@example.invalid"], check=True)
    (root / "README.md").write_text("synthetic\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "synthetic fixture"], check=True)
    return root


class TestGitEvidence(unittest.TestCase):
    def test_snapshot_is_read_only_and_omits_remotes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "repo")
            before = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain=v1"])
            _, snapshot = bind_repo(root)
            after = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain=v1"])
            self.assertEqual(before, after)
            self.assertTrue(snapshot["read_only"])
            self.assertFalse(snapshot["remote_urls_read"])
            self.assertNotIn(str(root), json.dumps(snapshot))

    def test_nested_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "repo")
            child = root / "child"
            child.mkdir()
            with self.assertRaises(UnsafePathError):
                bind_repo(child)

    def test_repository_parent_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "repo")
            with self.assertRaises(UnsafePathError):
                bind_repo(root / "child" / "..")

    @unittest.skipIf(os.name == "nt", "POSIX executable fixture")
    def test_project_git_and_redirecting_environment_are_never_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "repo")
            marker = root / "FAKE_GIT_RAN"
            fake = root / "git"
            fake.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 99\n", encoding="utf-8")
            fake.chmod(0o755)
            redirected = Path(tmp) / "not-a-repository"
            with mock.patch.dict(os.environ, {
                "PATH": f"{root}{os.pathsep}{os.environ.get('PATH', '')}",
                "GIT_DIR": str(redirected),
                "GIT_WORK_TREE": str(redirected),
                "GIT_INDEX_FILE": str(redirected / "index"),
            }, clear=False):
                _, snapshot = bind_repo(root)
            self.assertFalse(marker.exists())
            self.assertTrue(snapshot["git_executable_trusted"])
            self.assertTrue(snapshot["redirecting_git_environment_removed"])

    def test_snapshot_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            responses = [str(root), "false", "a" * 40, "", "README.md\0", "b" * 40, ""]
            with mock.patch("requirement_ledger.git_evidence._trusted_git",
                            return_value=Path("/usr/bin/git")), \
                    mock.patch("requirement_ledger.git_evidence._git", side_effect=responses):
                with self.assertRaises(InputChangedError):
                    bind_repo(root)


class TestPipeline(unittest.TestCase):
    ORACLE_DIGEST = "a" * 64
    def test_explicit_bundle_to_report_and_proposals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "repo")
            transcript = Path(tmp) / "transcript.md"
            transcript.write_text(
                "# User\nImprove it\n# Assistant\nDone\n# User\n"
                "That is not what I meant; keep the public API.\n",
                encoding="utf-8",
            )
            bundle = build_evidence_bundle(root, [transcript], provider="text",
                                           deterministic_key=b"test-key")
            self.assertEqual(bundle["kind"], "private-evidence")
            self.assertNotIn(str(root), json.dumps(bundle))
            observed = {item["kind"]: item["label"] for item in bundle["evidence"]}
            self.assertEqual(observed["user_message"], "SAID")
            self.assertEqual(observed["assistant_message"], "SAID")
            analysis = analyze_evidence(bundle)
            self.assertEqual(len(analysis["issues"]), 1)
            issue = analysis["issues"][0]
            self.assertEqual(issue["scope"], "unknown")
            self.assertNotEqual(issue["decision_status"], "confirmed")
            proposals = build_fix_proposals(analysis)
            self.assertEqual(proposals["status"], "DRAFT — NOT SENT")
            self.assertTrue(all(item["apply_status"] == "not-applied" for item in proposals["proposals"]))
            report = share_report(analysis)
            rendered = render_markdown_report(report)
            self.assertNotIn("keep the public API", rendered)
            self.assertIn("human must review", rendered)

    def test_incomplete_input_blocks_issue_decision(self) -> None:
        bundle = synthetic_demo_bundle()
        bundle["completeness"] = "incomplete"
        analysis = analyze_evidence(bundle)
        self.assertTrue(all(item["decision_status"] == "blocked" for item in analysis["issues"]))
        self.assertTrue(all(item["scope"] == "unknown" for item in analysis["issues"]))

    def test_single_complaint_never_confirms_upstream_or_personal(self) -> None:
        analysis = analyze_evidence(synthetic_demo_bundle())
        self.assertFalse(any(item["scope"] in ("upstream", "personal") for item in analysis["issues"]))

    def test_share_report_blocks_injected_sensitive_title(self) -> None:
        analysis = analyze_evidence(synthetic_demo_bundle())
        analysis["issues"][0]["title"] = "Contact person@example.test"
        report = share_report(analysis)
        self.assertNotIn("person@example.test", json.dumps(report))
        self.assertEqual(report["issues"][0]["title"], "Evidence item requires review")

    def test_share_report_drops_unrecognised_count_keys(self) -> None:
        analysis = analyze_evidence(synthetic_demo_bundle())
        analysis["counts"] = {"person@example.test": 1}
        report = share_report(analysis)
        self.assertEqual(report["summary"]["counts"], {})

    def test_validation_truth_table(self) -> None:
        record = lambda code: {"oracle": "oracle", "oracle_digest": self.ORACLE_DIGEST,
                               "exit_code": code}
        improved = validate_outcomes("oracle", self.ORACLE_DIGEST, record(1), record(0))
        self.assertEqual(improved["result"]["status"], "improved")
        regressed = validate_outcomes("oracle", self.ORACLE_DIGEST, record(0), record(1))
        self.assertEqual(regressed["result"]["status"], "regressed")
        inconclusive = validate_outcomes(
            "oracle", self.ORACLE_DIGEST,
            {"oracle": "other", "oracle_digest": self.ORACLE_DIGEST, "exit_code": 1},
            record(0),
        )
        self.assertEqual(inconclusive["result"]["status"], "inconclusive")

    def test_validation_rejects_boolean_unbounded_and_unbound_records(self) -> None:
        valid = {"oracle": "oracle", "oracle_digest": self.ORACLE_DIGEST, "exit_code": 0}
        for value in (True, False, -1, 256, "0", None):
            malformed = {"oracle": "oracle", "oracle_digest": self.ORACLE_DIGEST,
                         "exit_code": value}
            result = validate_outcomes("oracle", self.ORACLE_DIGEST, malformed, valid)
            self.assertEqual(result["result"]["status"], "inconclusive")
        mismatch = dict(valid, oracle_digest="b" * 64)
        self.assertEqual(validate_outcomes("oracle", self.ORACLE_DIGEST, mismatch, valid)
                         ["result"]["status"], "inconclusive")
        self.assertEqual(validate_outcomes("oracle", "not-a-digest", valid, valid)
                         ["result"]["status"], "inconclusive")

    def test_test_log_hash_and_parse_share_one_stable_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "test.log"
            payload = b"FAILED synthetic case\n"
            log.write_bytes(payload)
            digest, byte_count, events, completeness = pipeline_module._read_test_log_stable(log)
            self.assertEqual(digest, __import__("hashlib").sha256(payload).hexdigest())
            self.assertEqual(byte_count, len(payload))
            self.assertEqual(events[0]["private_text"], "FAILED synthetic case")
            self.assertEqual(completeness, "complete")

    def test_test_log_snapshot_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "test.log"
            log.write_text("FAILED synthetic case\n", encoding="utf-8")
            stable = (1, 2, 3, 1, 22, 4, 5)
            changed = (1, 2, 3, 1, 23, 6, 7)
            with mock.patch("requirement_ledger.pipeline._input_stat_signature",
                            side_effect=[stable, stable, stable, changed]):
                with self.assertRaises(InputChangedError):
                    pipeline_module._read_test_log_stable(log)
