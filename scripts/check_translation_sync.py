#!/usr/bin/env python3
"""Keep the Chinese mirror honest about how stale it is.

`SKILL.md` and `references/*.md` are normative.  Each `*.zh-CN.md` is a translation that
carries a stamp naming its source and that source's SHA256 at translation time:

    <!-- translation-of: SKILL.md sha256:0f1e2d... -->

This script recomputes the source hash and compares the document skeleton (heading levels
and fenced-code-block count), so drift is caught mechanically instead of by discipline.
It cannot judge whether the prose still means the same thing.

    python3 scripts/check_translation_sync.py            # report
    python3 scripts/check_translation_sync.py --update    # re-stamp after translating

Exit 0 prints TRANSLATIONS_IN_SYNC.  Exit 1 lists findings.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

SUFFIX = ".zh-CN.md"
STAMP = re.compile(
    r"<!--\s*translation-of:\s*(?P<source>[^\s]+)\s+sha256:(?P<digest>[0-9a-f]{8,64})\s*-->"
)
STAMP_TEMPLATE = "<!-- translation-of: {source} sha256:{digest} -->"
HEADING = re.compile(r"^(#{1,6})\s+\S")
FENCE = re.compile(r"^\s*```")
SEARCH_DIRS = (".", "references", "templates")
DIGEST_LEN = 16


def sha256_short(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:DIGEST_LEN]


def skeleton(text: str) -> tuple[tuple[int, ...], int]:
    """Heading levels in order, plus the number of fenced code blocks."""
    levels: list[int] = []
    fences = 0
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            if in_fence:
                fences += 1
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if match:
            levels.append(len(match.group(1)))
    return tuple(levels), fences


def translations(root: Path) -> list[Path]:
    found: list[Path] = []
    for name in SEARCH_DIRS:
        directory = root / name
        if directory.is_dir():
            found.extend(sorted(directory.glob(f"*{SUFFIX}")))
    return found


def sources(root: Path) -> list[Path]:
    found: list[Path] = []
    for name in SEARCH_DIRS:
        directory = root / name
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            if not path.name.endswith(SUFFIX):
                found.append(path)
    return found


def check(root: Path, *, update: bool = False) -> list[str]:
    findings: list[str] = []
    translated_sources: set[Path] = set()

    for mirror in translations(root):
        text = mirror.read_text(encoding="utf-8")
        stamp = STAMP.search(text)
        if not stamp:
            findings.append(f"{mirror.relative_to(root)}: no translation-of stamp")
            continue

        source = (root / stamp.group("source")).resolve()
        if not source.is_file():
            findings.append(
                f"{mirror.relative_to(root)}: stamp names a missing source "
                f"({stamp.group('source')})"
            )
            continue
        translated_sources.add(source)

        current = sha256_short(source)
        if stamp.group("digest") != current:
            if update:
                replacement = STAMP_TEMPLATE.format(
                    source=stamp.group("source"), digest=current
                )
                mirror.write_text(
                    text[: stamp.start()] + replacement + text[stamp.end():], encoding="utf-8"
                )
                print(f"RESTAMPED {mirror.relative_to(root)} -> {current}")
            else:
                findings.append(
                    f"{mirror.relative_to(root)}: STALE — {stamp.group('source')} changed since "
                    f"translation (stamp {stamp.group('digest')}, now {current})"
                )

        want, want_fences = skeleton(source.read_text(encoding="utf-8"))
        got, got_fences = skeleton(text)
        if want != got:
            findings.append(
                f"{mirror.relative_to(root)}: heading skeleton differs from "
                f"{stamp.group('source')} ({len(want)} headings vs {len(got)})"
            )
        if want_fences != got_fences:
            findings.append(
                f"{mirror.relative_to(root)}: {want_fences} code blocks in source, "
                f"{got_fences} in translation"
            )

    for source in sources(root):
        if source.resolve() not in translated_sources:
            expected = source.with_name(source.name[: -len(".md")] + SUFFIX)
            if not expected.is_file():
                findings.append(f"{source.relative_to(root)}: no {SUFFIX} translation")

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument(
        "--update", action="store_true", help="re-stamp mirrors with the current source hash"
    )
    args = parser.parse_args(argv)

    if not args.root.is_dir():
        print(f"not a directory: {args.root}", file=sys.stderr)
        return 2

    findings = check(args.root.resolve(), update=args.update)
    if findings:
        print("TRANSLATIONS_DRIFTED")
        for finding in findings:
            print(f"  - {finding}")
        return 1

    print("TRANSLATIONS_IN_SYNC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
