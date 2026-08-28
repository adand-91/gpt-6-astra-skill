"""Conservative redaction and a fail-closed gate for share-facing artefacts.

Passing this scanner is never described as proof that a file is safe.  It is one automated
check before a human review.  Findings expose categories and counts, never matched values.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

from .errors import PrivacyBlockError

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("authorization", re.compile(r"(?i)\b(?:authorization|proxy-authorization)\s*:\s*\S+")),
    ("cookie", re.compile(r"(?i)\b(?:cookie|set-cookie)\s*:\s*[^\r\n]+")),
    ("known_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16})\b")),
    ("assigned_secret", re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|passwd|secret)\s*[:=]\s*['\"]?[^\s'\"]{6,}")),
    ("email", re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.IGNORECASE)),
    ("phone", re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)|(?<!\d)\+\d{1,3}[- ]?(?:\d[- ]?){7,13}\d(?!\d)")),
    ("unix_home", re.compile(r"/(?:Users|home)/[^/\s]+")),
    ("windows_home", re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+")),
    ("private_remote", re.compile(r"(?i)(?:git@|ssh://|https?://[^\s/@:]+:[^\s/@]+@)[^\s]+")),
    ("uuid", re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b")),
    ("ip_address", re.compile(r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?!\d)")),
    ("ansi_control", re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")),
)


def finding_counts(text: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for category, pattern in _PATTERNS:
        counts[category] += sum(1 for _ in pattern.finditer(text))
    return {key: value for key, value in sorted(counts.items()) if value}


def redact_text(text: str) -> tuple[str, dict[str, int]]:
    counts: Counter[str] = Counter()
    redacted = text
    for category, pattern in _PATTERNS:
        def replace(match: re.Match[str], name: str = category) -> str:
            counts[name] += 1
            return f"<REDACTED:{name.upper()}>"

        redacted = pattern.sub(replace, redacted)
    return redacted, {key: value for key, value in sorted(counts.items()) if value}


def inspect_value(value: Any) -> dict[str, int]:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return finding_counts(rendered)


def assert_automated_privacy_check(value: Any) -> None:
    findings = inspect_value(value)
    if findings:
        categories = ", ".join(f"{name}={count}" for name, count in findings.items())
        raise PrivacyBlockError(
            "share-facing output failed the automated privacy check; "
            f"categories only: {categories}. No file was written."
        )


def manifest_for_private_texts(texts: list[str]) -> dict[str, Any]:
    total: Counter[str] = Counter()
    for text in texts:
        total.update(finding_counts(text))
    return {
        "automated_findings": dict(sorted(total.items())),
        "manifest_contains_original_values": False,
        "statement": "Category counts only; this is not a declaration that data is safe to share.",
    }
