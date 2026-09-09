#!/usr/bin/env python3
"""Check the mechanical shape of a Chinese Jarvis report.

This is a regression guard for repository fixtures.  It does not assess whether claims are true,
whether a recommendation is good, or whether a cited test really ran.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_MARKERS = ("# 项目总目标", "## 项目总进度", "当前工作区域：", "## 当前区域进度", "# 下一步")
DAILY = ("已核实结果", "未完成工作", "发现的问题", "先前改动", "候选优化", "唯一下一步", "读取范围与未知")
WEEKLY = ("周期趋势", "优化结果", "重复问题与延续事项", "候选状态与保留项", "维护健康度", "GitHub 与行业", "下一周期", "读取范围与未知")
EVIDENCE = re.compile(r"依据|证据|来源|测试|验收|文件|检查点|里程碑|权重|实测|observed|evidence", re.I)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
PERCENT = re.compile(r"(?<!\d)(\d{1,3})\s*%")
BAR = re.compile(r"^[█░]+$")
LIST = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")


def _headings(lines: list[str]) -> list[tuple[int, int, str, str]]:
    out = []
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m:
            out.append((i, len(m.group(1)), m.group(2).strip(), line))
    return out


def _blank_findings(lines: list[str], headings: list[tuple[int, int, str, str]]) -> list[str]:
    findings: list[str] = []
    for i, _, _, _ in headings:
        if i and lines[i - 1].strip():
            findings.append(f"heading line {i + 1} must have a blank line before it")
        if i + 1 < len(lines) and lines[i + 1].strip():
            findings.append(f"heading line {i + 1} must have a blank line after it")
    return findings


def _list_findings(lines: list[str]) -> list[str]:
    findings: list[str] = []
    i = 0
    while i < len(lines):
        if not LIST.match(lines[i]):
            i += 1
            continue
        start = i
        while i + 1 < len(lines) and LIST.match(lines[i + 1]):
            i += 1
        end = i
        if start and lines[start - 1].strip():
            findings.append(f"list line {start + 1} must have a blank line before it")
        if end + 1 < len(lines) and lines[end + 1].strip():
            findings.append(f"list line {end + 1} must have a blank line after it")
        i += 1
    return findings


def _section(lines: list[str], start: int, headings: list[tuple[int, int, str, str]]) -> list[str]:
    ends = [i for i, *_ in headings if i > start]
    return lines[start + 1 : (min(ends) if ends else len(lines))]


def _progress(lines: list[str], start: int, label: str) -> list[str]:
    chunk = _section(lines, start, _headings(lines))
    # The percentage and evidence marker commonly live in the heading itself.
    text = "\n".join([lines[start], *chunk])
    findings: list[str] = []
    unlocked = "范围未锁定，无法计算" in text
    percentages = PERCENT.findall(text)
    bars = [line.strip() for line in chunk if BAR.fullmatch(line.strip())]
    if unlocked:
        if percentages or bars:
            findings.append(f"{label}: unlocked scope cannot include a percentage or progress bar")
        return findings
    if len(percentages) != 1:
        findings.append(f"{label}: expected exactly one integer percentage from 0 to 100")
    elif not 0 <= int(percentages[0]) <= 100:
        findings.append(f"{label}: percentage must be from 0 to 100")
    if len(bars) != 1:
        findings.append(f"{label}: expected exactly one ten-cell █░ progress bar")
    elif len(bars[0]) != 10:
        findings.append(f"{label}: progress bar must contain exactly 10 cells")
    elif len(percentages) == 1:
        expected = min(10, max(0, (int(percentages[0]) + 5) // 10))
        if bars[0].count("█") != expected:
            findings.append(f"{label}: bar fill does not round the percentage to the nearest cell")
    if not re.search(r"实测|估算", text):
        findings.append(f"{label}: mark progress as 实测 or 估算")
    if not EVIDENCE.search(text):
        findings.append(f"{label}: include a basis for the progress figure")
    return findings


def _ordered_sections(lines: list[str], names: tuple[str, ...], mode: str) -> list[str]:
    headings = _headings(lines)
    positions = []
    findings: list[str] = []
    for name in names:
        hits = [(i, title) for i, level, title, _ in headings if level == 2 and title == name]
        if not hits:
            findings.append(f"{mode}: missing required section {name}")
        elif len(hits) > 1:
            findings.append(f"{mode}: duplicate required section {name}")
        else:
            positions.append(hits[0][0])
    if positions != sorted(positions):
        findings.append(f"{mode}: required sections are out of order")
    return findings


def check_text(text: str, mode: str = "project") -> list[str]:
    """Return mechanical format findings; an empty list means the shape is valid."""
    if mode not in {"project", "daily", "weekly"}:
        return [f"unknown mode: {mode}"]
    if "```" in text:
        return ["code fences cannot disguise a complete report"]
    lines = text.splitlines()
    headings = _headings(lines)
    findings = _blank_findings(lines, headings)
    findings.extend(_list_findings(lines))
    if mode == "project":
        expected = ["项目总目标", "项目总进度", "当前区域进度", "下一步"]
        for title in expected:
            if not any(title == t or (title == "项目总进度" and t.startswith("项目总进度："))
                       or (title == "当前区域进度" and t.startswith("当前区域进度："))
                       for _, level, t, _ in headings if level in (1, 2)):
                findings.append(f"project: missing required heading {title}")
        positions = []
        for title in expected:
            hits = [(i, t) for i, level, t, _ in headings if level in (1, 2) and
                    (t == title or (title in ("项目总进度", "当前区域进度") and t.startswith(title + "：")))]
            if hits:
                positions.append(hits[0][0])
        if positions != sorted(positions):
            findings.append("project: required headings are out of order")
        if not any("当前工作区域：" in line for line in lines):
            findings.append("project: missing 当前工作区域：")
        if not any("当前卡点" in line for line in lines):
            findings.append("project: missing 当前卡点")
        if not any("你现在无需操作" in line or "需要你确定" in line for line in lines):
            findings.append("project: missing no-action or decision field")
        next_pos = next((i for i, _, t, _ in headings if t == "下一步"), None)
        if next_pos is not None:
            tail = "\n".join(lines[next_pos + 1 :])
            for field in ("用途：", "交付：", "完成标准：", "下次汇报："):
                if field not in tail:
                    findings.append(f"project: 下一步 missing {field}")
        for i, _, t, _ in headings:
            if t == "项目总进度" or t.startswith("项目总进度："):
                findings.extend(_progress(lines, i, "overall progress"))
            if t == "当前区域进度" or t.startswith("当前区域进度："):
                findings.extend(_progress(lines, i, "area progress"))
        if not any(line.startswith("项目阶段：") for line in lines):
            findings.append("project: missing 项目阶段：")
    else:
        names = DAILY if mode == "daily" else WEEKLY
        findings.extend(_ordered_sections(lines, names, mode))
        if any(t == "项目总目标" or t == "下一步" or t.startswith("项目总进度")
               or t.startswith("当前区域进度") for _, _, t, _ in headings):
            findings.append(f"{mode}: project report headings must not be mixed into {mode} mode")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="check Jarvis report format")
    parser.add_argument("report", type=Path)
    parser.add_argument("--mode", choices=("project", "daily", "weekly"), default="project")
    args = parser.parse_args(argv)
    try:
        text = args.report.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read: {exc}", file=sys.stderr)
        return 2
    findings = check_text(text, args.mode)
    if findings:
        print("INVALID_JARVIS_REPORT")
        print("\n".join(f"- {item}" for item in findings))
        return 1
    print("VALID_JARVIS_REPORT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
