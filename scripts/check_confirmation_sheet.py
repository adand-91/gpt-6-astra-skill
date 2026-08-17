#!/usr/bin/env python3
"""Mechanically validate a requirement confirmation sheet.

Checks form, never truth: a sheet can pass every check here and still describe the wrong
project.  That is what the user's confirmation is for.

Recognises English and Chinese field names and labels interchangeably, so a bilingual team
can keep one checker.

Exit 0 prints VALID_SHEET.  Exit 1 lists findings.  Exit 2 is a usage or IO error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# --- vocabulary -------------------------------------------------------------------------

# Order matters: the more specific name must be tested first, because "Out of scope"
# contains "scope" and "不包含" contains "包含".
FIELDS: list[tuple[str, tuple[str, ...]]] = [
    ("goal", ("goal", "目标")),
    ("out_of_scope", ("out of scope", "not in scope", "不包含", "不做")),
    ("in_scope", ("in scope", "scope", "包含", "交付物")),
    ("inputs", ("inputs", "input", "输入")),
    ("outputs", ("outputs", "output", "输出")),
    ("acceptance", ("acceptance", "验收")),
    ("constraints", ("constraints", "约束")),
    ("where_it_runs", ("where it runs", "runs on", "执行位置", "运行环境")),
    ("open_items", ("open items", "未确认项", "待确认项", "待确认")),
]

FIELD_ORDER = [key for key, _ in FIELDS]

LABELS: dict[str, tuple[str, ...]] = {
    "CONFIRMED": ("CONFIRMED", "已确认"),
    "INFERRED": ("INFERRED", "AI推断", "推断"),
    "OPEN": ("OPEN", "待确认"),
}

LOCK_NAMES = ("locked", "锁定")
LOCK_TRUE = ("yes", "true", "是", "已锁定", "locked")

MESSAGES = {
    "en": {
        "missing_field": "missing required field: {field}",
        "empty_field": "field has no items: {field}",
        "unlabelled": "{field}: item carries no label (CONFIRMED / INFERRED / OPEN): {item}",
        "double_label": "{field}: item carries {n} labels ({labels}), exactly one allowed: {item}",
        "open_without_owner": "{field}: OPEN item does not name who owes the answer: {item}",
        "open_not_listed": "{n} OPEN item(s) exist elsewhere but 'Open items' lists none",
        "no_lock_line": "no 'Locked:' line — a sheet relied on without a lock state is not a lock",
        "too_big": "sheet is {size} bytes, over the {limit}-byte one-screen budget",
        "promotion": "INFERRED -> CONFIRMED without a recorded confirmation: {item}",
        "promotion_hint": (
            "pass --promotions-approved once the user has confirmed these on the record"
        ),
        "valid": "VALID_SHEET",
        "invalid": "INVALID_SHEET",
        "locked_state": "lock state: {state}",
    },
    "zh": {
        "missing_field": "缺少必备字段：{field}",
        "empty_field": "字段没有任何条目：{field}",
        "unlabelled": "{field}：条目没有标签（已确认 / AI推断 / 待确认）：{item}",
        "double_label": "{field}：条目带了 {n} 个标签（{labels}），只允许一个：{item}",
        "open_without_owner": "{field}：待确认条目没写谁该给答案：{item}",
        "open_not_listed": "别处存在 {n} 个待确认条目，但「未确认项」里一个都没列",
        "no_lock_line": "没有「锁定:」行 —— 不写锁定状态就直接依赖的确认单不算已锁定",
        "too_big": "确认单 {size} 字节，超出一屏预算 {limit} 字节",
        "promotion": "AI推断 → 已确认，但没有在案的用户确认：{item}",
        "promotion_hint": "用户确认过之后加 --promotions-approved 再跑",
        "valid": "VALID_SHEET",
        "invalid": "INVALID_SHEET",
        "locked_state": "锁定状态：{state}",
    },
}

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
HEADING_TEXT = re.compile(r"^\s*(?:#{1,6}\s*)?\*{0,2}([^*:：#]+?)\*{0,2}\s*[:：]?\s*$")
OWNER_HINT = re.compile(r"(owner|owed by|waiting on|归属|负责人|等谁|等待)", re.IGNORECASE)


def strip_comments(text: str) -> str:
    return HTML_COMMENT.sub("", text)


def field_of(line: str) -> str | None:
    """Return the field key if this line is a field heading."""
    match = HEADING_TEXT.match(line.rstrip())
    if not match:
        return None
    name = match.group(1).strip().lower()
    if not name or len(name) > 40:
        return None
    for key, aliases in FIELDS:
        for alias in aliases:
            if alias in name:
                return key
    return None


def labels_in(item: str) -> list[str]:
    """Labels carried by one item.

    ASCII labels are matched case-sensitively and on word boundaries, because the lowercase
    words are ordinary English: "run X, open Y, see Z" is prose, not an OPEN item.
    """
    found = []
    for canonical, aliases in LABELS.items():
        for alias in aliases:
            if alias.isascii():
                hit = re.search(r"\b" + re.escape(alias) + r"\b", item) is not None
            else:
                hit = alias in item
            if hit:
                found.append(canonical)
                break
    return found


def normalise(item: str) -> str:
    """Item text with labels and punctuation stripped, for cross-revision comparison."""
    text = item
    for aliases in LABELS.values():
        for alias in aliases:
            if alias.isascii():
                text = re.sub(r"\b" + re.escape(alias) + r"\b", "", text)
            else:
                text = text.replace(alias, "")
    text = re.sub(r"[`*_\[\](){}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -—:：.。").lower()


def parse(text: str) -> tuple[dict[str, list[str]], str | None]:
    """Return {field: [items]} plus the raw lock line value, if any."""
    sections: dict[str, list[str]] = {}
    lock_value: str | None = None
    current: str | None = None

    for raw in strip_comments(text).splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue

        stripped = line.strip().lstrip("*_ ").rstrip("*_ ")
        for name in LOCK_NAMES:
            if stripped.lower().startswith(name):
                remainder = stripped[len(name):].lstrip(" :：*_")
                if remainder:
                    lock_value = remainder
                break

        bullet = BULLET.match(line)
        if bullet:
            if current:
                sections[current].append(bullet.group(1).strip())
            continue

        key = field_of(line)
        if key is not None:
            current = key
            sections.setdefault(key, [])

    return sections, lock_value


def check(
    text: str,
    *,
    lang: str = "en",
    max_bytes: int = 6000,
    baseline: str | None = None,
    promotions_approved: bool = False,
) -> list[str]:
    msg = MESSAGES[lang]
    findings: list[str] = []
    sections, lock_value = parse(text)

    size = len(text.encode("utf-8"))
    if size > max_bytes:
        findings.append(msg["too_big"].format(size=size, limit=max_bytes))

    open_elsewhere = 0
    for key in FIELD_ORDER:
        if key not in sections:
            findings.append(msg["missing_field"].format(field=key))
            continue
        items = sections[key]
        if not items:
            findings.append(msg["empty_field"].format(field=key))
            continue
        for item in items:
            found = labels_in(item)
            if not found:
                findings.append(msg["unlabelled"].format(field=key, item=item))
                continue
            if len(found) > 1:
                findings.append(
                    msg["double_label"].format(
                        field=key, n=len(found), labels=", ".join(sorted(found)), item=item
                    )
                )
                continue
            if found[0] == "OPEN":
                if key != "open_items":
                    open_elsewhere += 1
                if not OWNER_HINT.search(item):
                    findings.append(msg["open_without_owner"].format(field=key, item=item))

    if open_elsewhere:
        listed = sections.get("open_items", [])
        if not any(labels_in(i) == ["OPEN"] for i in listed):
            findings.append(msg["open_not_listed"].format(n=open_elsewhere))

    if lock_value is None:
        findings.append(msg["no_lock_line"])

    if baseline is not None and not promotions_approved:
        old_sections, _ = parse(baseline)
        old_labels: dict[str, str] = {}
        for items in old_sections.values():
            for item in items:
                found = labels_in(item)
                if len(found) == 1:
                    old_labels[normalise(item)] = found[0]
        promoted = []
        for items in sections.values():
            for item in items:
                found = labels_in(item)
                if len(found) == 1 and found[0] == "CONFIRMED":
                    if old_labels.get(normalise(item)) == "INFERRED":
                        promoted.append(item)
        for item in promoted:
            findings.append(msg["promotion"].format(item=item))
        if promoted:
            findings.append(msg["promotion_hint"])

    return findings


def is_locked(lock_value: str | None) -> bool:
    if not lock_value:
        return False
    head = lock_value.strip().lower()
    return any(head.startswith(t) for t in LOCK_TRUE)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--lang", choices=("en", "zh"), default="en")
    parser.add_argument("--max-bytes", type=int, default=6000)
    parser.add_argument(
        "--baseline", type=Path, help="earlier revision, to catch INFERRED -> CONFIRMED promotions"
    )
    parser.add_argument("--promotions-approved", action="store_true")
    args = parser.parse_args(argv)

    try:
        text = args.sheet.read_text(encoding="utf-8")
        baseline = args.baseline.read_text(encoding="utf-8") if args.baseline else None
    except OSError as exc:
        print(f"cannot read: {exc}", file=sys.stderr)
        return 2

    msg = MESSAGES[args.lang]
    findings = check(
        text,
        lang=args.lang,
        max_bytes=args.max_bytes,
        baseline=baseline,
        promotions_approved=args.promotions_approved,
    )

    if findings:
        print(msg["invalid"])
        for finding in findings:
            print(f"  - {finding}")
        return 1

    _, lock_value = parse(text)
    print(msg["valid"])
    print(msg["locked_state"].format(state="locked" if is_locked(lock_value) else lock_value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
