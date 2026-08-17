#!/usr/bin/env python3
"""Mechanically check a retrospective before anyone quotes it as fact.

Catches the failures that make a retrospective actively harmful: a number with no source, a
claim with no label, an inference dressed up as something the user said, an empty section
padded out to look complete.

Recognises English and Chinese section names and labels interchangeably.

Exit 0 prints VALID_RETRO.  Exit 1 lists findings.  Exit 2 is a usage or IO error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECTIONS: list[tuple[str, tuple[str, ...]]] = [
    ("measured", ("measured", "实测", "机械层", "数据")),
    ("real_requirement", ("real requirement", "真需求", "真实需求")),
    ("requirement_trail", ("requirement trail", "需求追踪", "需求流水", "需求去向")),
    ("mistakes", ("mistakes", "错误", "失误")),
    ("automation", ("automation", "自动化", "可自动化")),
    ("unknown", ("not done", "unknown", "未完成", "未知", "待确认")),
    ("next", ("next single action", "next action", "下一个动作", "下一步")),
]

LABELS = {
    "SAID": ("SAID", "原话", "用户说"),
    "INFERRED": ("INFERRED", "推断"),
    "UNKNOWN": ("UNKNOWN", "未知"),
}

# A bare figure in a claim needs a provenance marker: (facts), a path, a timestamp, or a
# table cell that names its own source.
SOURCE_HINT = re.compile(
    r"\(facts\)|facts\.json|\(scanner\)|scan_transcript|/[\w./-]+"
    r"|\d{4}-\d{2}-\d{2}|(?<![\d-])\d{1,2}-\d{2}(?![\d-])"   # 2026-08-17 and bare 08-17
    r"|（facts）|来自脚本|脚本输出",
    re.IGNORECASE,
)
# Only *quantitative* claims need a source. A bare small integer is usually a table row index
# or a zero cost, and demanding provenance for those trains people to ignore the checker.
NUMBER = re.compile(
    r"(?<![\w.-])\d{2,}[\d,]*(?:\.\d+)?"
    r"|(?<![\w.-])\d+\s*(?:[x×]|次|轮|个|条|%|turns?|calls?|sessions?|messages?)"
    r"|[x×]\s*\d+",
    re.IGNORECASE,
)
ROW_INDEX = re.compile(r"^\d{1,3}$")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
HEADING = re.compile(r"^\s*(#{1,6})\s+(.*?)\s*$")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
TABLE_DIVIDER = re.compile(r"^\s*\|[\s|:-]+\|\s*$")

# Words that make a claim quantitative without a countable number; these need a source too.
VAGUE_QUANTITY = ("most of", "majority", "much of", "nearly all", "hardly any",
                  "大部分", "多数", "几乎全部", "绝大多数", "大多")

MESSAGES = {
    "en": {
        "missing_section": "missing required section: {name}",
        "empty_section": "section has no content: {name}",
        "unlabelled": "{name}: claim carries no SAID / INFERRED / UNKNOWN label: {line}",
        "number_no_source": "{name}: number with no source — add (facts), a path, or a date: {line}",
        "vague_quantity": "{name}: quantity word with no measurement: {line}",
        "no_window": "no window in the frontmatter — a retrospective without a window and offset "
                     "gets filed against the wrong work",
        "no_offset": "window has no UTC offset: {value}",
        "valid": "VALID_RETRO",
        "invalid": "INVALID_RETRO",
        "counts": "sections {sections}, labelled claims {labelled}, sourced numbers {sourced}",
    },
    "zh": {
        "missing_section": "缺少必备小节：{name}",
        "empty_section": "小节没有任何内容：{name}",
        "unlabelled": "{name}：这条没有 原话 / 推断 / 未知 标签：{line}",
        "number_no_source": "{name}：数字没有出处 —— 补 (facts)、路径或日期：{line}",
        "vague_quantity": "{name}：用了程度词但没有实测数字：{line}",
        "no_window": "frontmatter 里没有窗口 —— 不写窗口和时区的复盘会被归到错误的日期上",
        "no_offset": "窗口没写时区偏移：{value}",
        "valid": "VALID_RETRO",
        "invalid": "INVALID_RETRO",
        "counts": "小节 {sections} 个，带标签结论 {labelled} 条，有出处数字 {sourced} 处",
    },
}


def strip_noise(text: str) -> tuple[str, str]:
    """Return (frontmatter, body) with HTML comments removed from the body."""
    match = FRONTMATTER.match(text)
    front = match.group(0) if match else ""
    body = text[len(front):]
    return front, HTML_COMMENT.sub("", body)


def section_of(line: str) -> str | None:
    match = HEADING.match(line)
    if not match:
        return None
    name = match.group(2).strip().lower().lstrip("#").strip()
    name = re.sub(r"[—\-–:：].*$", "", name).strip() or match.group(2).strip().lower()
    for key, aliases in SECTIONS:
        for alias in aliases:
            if alias in name:
                return key
    return "other"


def labels_in(text: str) -> list[str]:
    found = []
    for canonical, aliases in LABELS.items():
        for alias in aliases:
            hit = (re.search(r"\b" + re.escape(alias) + r"\b", text) is not None
                   if alias.isascii() else alias in text)
            if hit:
                found.append(canonical)
                break
    return found


HEADER_CELLS = {"", "cost", "layer", "fix", "#", "repeats", "pattern", "verdict", "why",
                "requirement", "ended as", "evidence", "what happened", "代价", "层级",
                "修法", "次数", "结论", "依据", "需求", "去向"}


def claims(body: str) -> tuple[list[tuple[str, str]], dict[str, int]]:
    """Return (claims, content_lines_per_section).

    A claim is a bullet or a table data row -- the things that assert something and therefore
    need a label and a source.  Plain prose still counts as content, so a section written as a
    paragraph is not reported as empty.
    """
    out: list[tuple[str, str]] = []
    content: dict[str, int] = {}
    current = "other"
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        key = section_of(line)
        if key is not None:
            current = key
            content.setdefault(current, 0)
            continue
        if TABLE_DIVIDER.match(line):
            continue
        content[current] = content.get(current, 0) + 1

        bullet = BULLET.match(line)
        if bullet:
            out.append((current, bullet.group(1).strip()))
            continue
        row = TABLE_ROW.match(line)
        if row:
            cells = [c.strip() for c in row.group(1).split("|")]
            if not any(cells) or all(c.lower() in HEADER_CELLS for c in cells):
                continue
            # Drop a leading row index so '| 3 | ... |' is not read as the number three.
            if cells and ROW_INDEX.match(cells[0]):
                cells = cells[1:]
            out.append((current, " | ".join(cells)))
    return out, content


def present_sections(body: str) -> set[str]:
    return {k for k in (section_of(l) for l in body.splitlines()) if k and k != "other"}


def check(text: str, *, lang: str = "en") -> tuple[list[str], dict[str, int]]:
    msg = MESSAGES[lang]
    findings: list[str] = []
    front, body = strip_noise(text)

    window = re.search(r"^window\s*:\s*(.+)$", front, re.MULTILINE | re.IGNORECASE)
    if not window:
        findings.append(msg["no_window"])
    elif not re.search(r"[+-]\d{2}:?\d{2}|\bZ\b|UTC", window.group(1)):
        findings.append(msg["no_offset"].format(value=window.group(1).strip()))

    found_sections = present_sections(body)
    for key, aliases in SECTIONS:
        if key not in found_sections:
            findings.append(msg["missing_section"].format(name=aliases[0]))

    found_claims, content = claims(body)
    labelled = sourced = 0
    for key, claim in found_claims:
        has_source = SOURCE_HINT.search(claim) is not None
        found_labels = labels_in(claim)

        if key in ("real_requirement", "unknown"):
            if not found_labels:
                findings.append(msg["unlabelled"].format(name=key, line=claim[:110]))
            else:
                labelled += 1
        elif found_labels:
            labelled += 1

        if key == "measured" or NUMBER.search(claim):
            if NUMBER.search(claim) and not has_source and "UNKNOWN" not in found_labels:
                findings.append(msg["number_no_source"].format(name=key, line=claim[:110]))
            elif has_source:
                sourced += 1

        low = claim.lower()
        if any(v in low for v in VAGUE_QUANTITY) and not has_source:
            findings.append(msg["vague_quantity"].format(name=key, line=claim[:110]))

    for key, aliases in SECTIONS:
        if key in found_sections and content.get(key, 0) == 0:
            findings.append(msg["empty_section"].format(name=aliases[0]))

    return findings, {"sections": len(found_sections), "labelled": labelled, "sourced": sourced}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", type=Path)
    parser.add_argument("--lang", choices=("en", "zh"), default="en")
    args = parser.parse_args(argv)

    try:
        text = args.report.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read: {exc}", file=sys.stderr)
        return 2

    msg = MESSAGES[args.lang]
    findings, counts = check(text, lang=args.lang)
    if findings:
        print(msg["invalid"])
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print(msg["valid"])
    print("  " + msg["counts"].format(**counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
