#!/usr/bin/env python3
"""Perform heuristic static checks over editable Skill metadata.

This deliberately small parser recognizes common description forms. It is not a general YAML
parser and a PASS or REVIEW result is not evidence that a Skill behaves correctly with GPT-6.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def frontmatter(text: str) -> list[str] | None:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            return lines[1:index]
    return None


_FIELD = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")


def _fields(lines: list[str]) -> list[tuple[str, str, int, int]]:
    starts = [(index, match) for index, line in enumerate(lines) if (match := _FIELD.match(line))]
    fields: list[tuple[str, str, int, int]] = []
    for position, (start, match) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        fields.append((match.group(1), match.group(2) or "", start, end))
    return fields


def _inline_description(value: str) -> tuple[str, bool]:
    value = value.strip()
    if not value:
        return "", False
    if value[0] not in "\"'":
        # Descriptions are expected to be simple text. Do not guess YAML collections, anchors,
        # tags, special scalars, comments, or colon-containing plain scalars.
        if (
            value[0] in "[{&*!?"
            or "#" in value
            or ":" in value
            or value.casefold() in {"~", "null", "true", "false", "yes", "no", "on", "off"}
            or re.fullmatch(r"[-+]?(?:\d[\d_]*(?:\.\d[\d_]*)?|\.\d[\d_]*)(?:e[-+]?\d+)?", value, re.I)
        ):
            return "", True
        return value, False
    if len(value) < 2 or value[-1] != value[0]:
        return "", True
    return value[1:-1], False


def description(text: str) -> tuple[str, str]:
    """Return (value, state) for inline, quoted, >, >-, |, and |- descriptions.

    Other YAML syntax is left for manual_review rather than reported as a missing description.
    """
    metadata = frontmatter(text)
    if metadata is None:
        return "", "missing"
    descriptions = [field for field in _fields(metadata) if field[0] == "description"]
    if not descriptions:
        return "", "missing"
    if len(descriptions) != 1:
        return "", "manual_review"

    _, value, start, end = descriptions[0]
    value = value.strip()
    if not value:
        return "", "missing"
    if value[0] not in ">|":
        # Plain/quoted YAML can continue on later lines. We do not parse that form; never
        # certify only its first line while silently dropping the rest of the description.
        if any(line.strip() for line in metadata[start + 1:end]):
            return "", "manual_review"
        result, needs_review = _inline_description(value)
        return result, "manual_review" if needs_review else ("ok" if result else "missing")

    if not re.fullmatch(r"[>|][+-]?", value):
        return "", "manual_review"
    content = metadata[start + 1:end]
    if not content or any(line and not line[0].isspace() for line in content):
        return "", "manual_review"
    stripped = [line.strip() for line in content]
    if not any(stripped):
        return "", "missing"
    if value[0] == ">":
        return " ".join(line for line in stripped if line), "ok"
    return "\n".join(stripped).strip(), "ok"


def audit(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    metadata = frontmatter(text)
    desc, description_state = description(text)
    findings: list[str] = []
    if metadata is None:
        findings.append("missing_frontmatter")
    if metadata is None or not any(
        name == "name" and value.strip() for name, value, _, _ in _fields(metadata)
    ):
        findings.append("missing_name")
    if description_state == "missing":
        findings.append("missing_description")
    elif description_state == "manual_review":
        findings.append("description_manual_review")
    elif len(desc) > 420:
        # 420 is a local readability heuristic, not an OpenAI requirement.
        findings.append("description_length_review")
    if not re.search(r"输入|input", text, re.I):
        findings.append("input_contract_review")
    if not re.search(r"输出|output", text, re.I):
        findings.append("output_contract_review")
    if not re.search(r"完成标准|验收|quality|check", text, re.I):
        findings.append("completion_check_review")
    if not re.search(r"不要用于|不适用|边界|scope|boundary", text, re.I):
        findings.append("boundary_review")
    return {
        "path": str(path),
        "lines": len(text.splitlines()),
        "description_chars": len(desc),
        "findings": findings,
        "status": "REVIEW" if findings else "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Heuristic static Skill metadata audit; not a model-behavior certification.",
        epilog="The 420-character description review is a local readability heuristic, not an OpenAI requirement.",
    )
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    files: list[Path] = []
    for root in args.roots:
        if root.is_file() and root.name == "SKILL.md":
            files.append(root)
        elif root.is_dir():
            files.extend(sorted(root.rglob("SKILL.md")))
    results = [audit(path) for path in sorted(set(files))]
    if not results:
        parser.error("no SKILL.md files found in the supplied roots")
    payload = {
        "audit_kind": "heuristic_static",
        "disclaimer": "Metadata findings are not a GPT-6 behavior certification.",
        "description_length_threshold": (
            "420 characters is a local readability heuristic, not an OpenAI requirement."
        ),
        "count": len(results),
        "results": results,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in results:
        suffix = ", ".join(item["findings"]) or "ok"
        print(f"{item['status']}\t{item['description_chars']} chars\t{item['path']}\t{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
