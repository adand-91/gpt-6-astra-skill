#!/usr/bin/env python3
"""Turn agent transcripts into countable facts, so a retrospective rests on evidence.

Reads Claude Code and Codex session files (or a plain-text transcript) and emits what a
model must not estimate by eye: how many real user turns there were, what the user said
verbatim, where they corrected course, which tool calls failed, and which command patterns
repeat often enough to be worth automating.

The model's job is interpretation.  Counting is this script's job.  A retrospective that
guesses numbers from memory is a failed retrospective.

Hard limits, because real transcripts are hostile:
  * streams line by line; never loads a file whole (sessions of 250 MB exist)
  * a single line can be 1.5 M characters of base64 image; oversized lines are measured,
    not parsed
  * base64 payloads are never decoded, only typed and sized

    python3 scan_transcript.py --engine claude --since 7d
    python3 scan_transcript.py --engine both --since 7d --format json --out facts.json
    python3 scan_transcript.py path/to/session.jsonl
    python3 scan_transcript.py --engine claude --since 7d --no-text   # omit bodies; still private

Exit 0 on success, 2 on usage/IO error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

MAX_LINE_BYTES = 200_000
MAX_MESSAGE_CHARS = 4_000
MAX_MESSAGES_PER_SESSION = 400
REPEAT_MIN = 3
NGRAM_SIZE = 3

CLAUDE_ROOT = Path.home() / ".claude" / "projects"
CODEX_ROOT = Path.home() / ".codex" / "sessions"

# Course corrections are the highest-value signal for the real requirement: they mark the
# moments where what the agent was doing diverged from what the user wanted.  These are
# recall candidates only -- the model still has to judge each one.
CORRECTION_MARKERS = (
    "不对", "不是这", "不是我", "错了", "搞错", "改成", "重新", "回退", "撤销", "别再",
    "不要", "先停", "停一下", "我说的是", "我要的是", "不是让你", "谁让你", "又错",
    "重来", "白做", "跑偏", "理解错", "反了", "不用管", "发错",
    "that's not", "thats not", "not what i", "i said", "i meant", "instead of",
    "no, ", "nope", "wrong", "revert", "undo", "roll back", "rollback",
    "stop ", "don't ", "dont ", "actually no", "start over",
)

WS = re.compile(r"\s+")
ARG = re.compile(r"""(["'])(?:\\.|(?!\1).)*\1|/\S+|--?\w[\w-]*=?\S*|\b\d[\d.]*\b""")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_when(value: str | None) -> datetime | None:
    """Accept an ISO timestamp or a relative '7d' / '36h' / '90m' window."""
    if not value:
        return None
    text = value.strip()
    match = re.fullmatch(r"(\d+)\s*([dhm])", text, re.IGNORECASE)
    if match:
        n = int(match.group(1))
        unit = {"d": "days", "h": "hours", "m": "minutes"}[match.group(2).lower()]
        return now_utc() - timedelta(**{unit: n})
    text = text.replace("Z", "+00:00")
    try:
        stamp = datetime.fromisoformat(text)
    except ValueError:
        raise SystemExit(f"cannot read a time from {value!r}; use ISO or 7d / 36h / 90m")
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)


def line_time(raw: Any) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        stamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)


def clip(text: str) -> str:
    text = text.strip()
    if len(text) <= MAX_MESSAGE_CHARS:
        return text
    return text[:MAX_MESSAGE_CHARS] + f"…[+{len(text) - MAX_MESSAGE_CHARS} chars]"


def is_correction(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in CORRECTION_MARKERS)


def command_shape(command: str) -> str:
    """Collapse a shell command to its shape, so repeats are visible across runs.

    'python3 /a/b/gen.py --out /tmp/x --seed 7'  ->  'python3 <path> --out= <path> <n>'
    Two invocations that differ only in paths and numbers share a shape.
    """
    collapsed = ARG.sub(lambda m: "<path>" if m.group(0).startswith("/") else "<arg>", command)
    return WS.sub(" ", collapsed).strip()[:160]


def iter_lines(path: Path) -> Iterator[tuple[int, str | None]]:
    """Yield (byte_length, text) per line; text is None when the line is too big to parse."""
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            size = len(raw.encode("utf-8", errors="replace"))
            yield (size, None if size > MAX_LINE_BYTES else raw)


def blank_facts(path: Path, engine: str) -> dict[str, Any]:
    return {
        "engine": engine,
        "path": str(path),
        "session": path.stem,
        "bytes": path.stat().st_size,
        "first_seen": None,
        "last_seen": None,
        "cwd": None,
        "counts": {
            "user_turns": 0,
            "assistant_turns": 0,
            "tool_calls": 0,
            "tool_errors": 0,
            "images": 0,
            "thinking_blocks": 0,
            "oversized_lines": 0,
            "unparsable_lines": 0,
            "sidechain_turns": 0,
            "compactions": 0,
        },
        "tools": Counter(),
        "errors": [],
        "user_messages": [],
        "corrections": [],
        "command_shapes": Counter(),
        "tool_sequence": [],
    }


def note_time(facts: dict[str, Any], stamp: datetime | None) -> None:
    if stamp is None:
        return
    iso = stamp.isoformat()
    if facts["first_seen"] is None or iso < facts["first_seen"]:
        facts["first_seen"] = iso
    if facts["last_seen"] is None or iso > facts["last_seen"]:
        facts["last_seen"] = iso


def add_user_message(facts: dict[str, Any], text: str, stamp: datetime | None) -> None:
    text = clip(text)
    if not text:
        return
    facts["counts"]["user_turns"] += 1
    entry = {"at": stamp.isoformat() if stamp else None, "text": text}
    if len(facts["user_messages"]) < MAX_MESSAGES_PER_SESSION:
        facts["user_messages"].append(entry)
    if is_correction(text):
        facts["corrections"].append(entry)


def add_tool_call(facts: dict[str, Any], name: str, payload: Any) -> None:
    facts["counts"]["tool_calls"] += 1
    facts["tools"][name] += 1
    facts["tool_sequence"].append(name)
    command = None
    if isinstance(payload, dict):
        command = payload.get("command") or payload.get("cmd")
    elif isinstance(payload, str) and payload.strip().startswith("{"):
        try:
            command = (json.loads(payload) or {}).get("command")
        except (ValueError, AttributeError):
            command = None
    if isinstance(command, list):
        command = " ".join(str(c) for c in command)
    if isinstance(command, str) and command.strip():
        facts["command_shapes"][command_shape(command)] += 1


def add_error(facts: dict[str, Any], tool: str, text: str) -> None:
    facts["counts"]["tool_errors"] += 1
    if len(facts["errors"]) < 60:
        facts["errors"].append({"tool": tool, "text": clip(str(text))[:400]})


# --- Claude Code -----------------------------------------------------------------------
#
# Note the trap: tool results come back as type "user" with tool_result blocks.  Counting
# those as user turns inflates a 900-turn session out of a 40-turn conversation, and
# poisons the real-requirement extraction with tool output.

def parse_claude(path: Path) -> dict[str, Any]:
    facts = blank_facts(path, "claude")
    pending: dict[str, str] = {}

    for size, raw in iter_lines(path):
        if raw is None:
            facts["counts"]["oversized_lines"] += 1
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            facts["counts"]["unparsable_lines"] += 1
            continue
        if not isinstance(entry, dict):
            continue

        stamp = line_time(entry.get("timestamp"))
        note_time(facts, stamp)
        if facts["cwd"] is None and entry.get("cwd"):
            facts["cwd"] = entry["cwd"]
        if entry.get("isSidechain"):
            facts["counts"]["sidechain_turns"] += 1
            continue
        if entry.get("isMeta"):
            continue

        kind = entry.get("type")
        if kind == "system" and "compact" in str(entry.get("subtype", "")).lower():
            facts["counts"]["compactions"] += 1
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        role = message.get("role")

        if isinstance(content, str):
            if role == "user" and kind == "user":
                add_user_message(facts, content, stamp)
            elif role == "assistant":
                facts["counts"]["assistant_turns"] += 1
            continue
        if not isinstance(content, list):
            continue

        texts: list[str] = []
        had_tool_result = False
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                texts.append(str(block.get("text", "")))
            elif btype == "thinking":
                facts["counts"]["thinking_blocks"] += 1
            elif btype == "image":
                facts["counts"]["images"] += 1
            elif btype == "tool_use":
                name = str(block.get("name", "?"))
                pending[str(block.get("id"))] = name
                add_tool_call(facts, name, block.get("input"))
            elif btype == "tool_result":
                had_tool_result = True
                if block.get("is_error"):
                    tool = pending.get(str(block.get("tool_use_id")), "?")
                    add_error(facts, tool, summarise_result(block.get("content")))

        if role == "assistant":
            facts["counts"]["assistant_turns"] += 1
        elif role == "user" and not had_tool_result:
            add_user_message(facts, "\n".join(t for t in texts if t), stamp)

    return facts


def summarise_result(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [str(b.get("text", "")) for b in content if isinstance(b, dict)]
        return " ".join(p for p in parts if p)
    return str(content)


# --- Codex -----------------------------------------------------------------------------
#
# Real typed input is event_msg/user_message.  response_item/message with role user also
# carries injected context, so it is only a fallback when no event_msg was recorded.

def parse_codex(path: Path) -> dict[str, Any]:
    facts = blank_facts(path, "codex")
    saw_event_user = False
    fallback: list[tuple[str, datetime | None]] = []
    calls: dict[str, str] = {}

    for size, raw in iter_lines(path):
        if raw is None:
            facts["counts"]["oversized_lines"] += 1
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            facts["counts"]["unparsable_lines"] += 1
            continue
        if not isinstance(entry, dict):
            continue

        stamp = line_time(entry.get("timestamp"))
        note_time(facts, stamp)
        kind = entry.get("type")
        payload = entry.get("payload")
        if not isinstance(payload, dict):
            continue
        ptype = payload.get("type")

        if kind == "session_meta":
            facts["cwd"] = facts["cwd"] or payload.get("cwd")
            continue
        if kind == "compacted":
            facts["counts"]["compactions"] += 1
            continue

        if kind == "event_msg":
            if ptype == "user_message":
                saw_event_user = True
                add_user_message(facts, str(payload.get("message") or ""), stamp)
                for key in ("images", "local_images"):
                    got = payload.get(key)
                    if isinstance(got, list):
                        facts["counts"]["images"] += len(got)
            elif ptype == "agent_message":
                facts["counts"]["assistant_turns"] += 1
            elif ptype == "agent_reasoning":
                facts["counts"]["thinking_blocks"] += 1
            elif ptype == "patch_apply_end" and payload.get("success") is False:
                add_error(facts, "patch_apply", payload.get("stderr") or "patch failed")
            continue

        if kind != "response_item":
            continue

        if ptype in ("function_call", "custom_tool_call"):
            name = str(payload.get("name", "?"))
            calls[str(payload.get("call_id"))] = name
            add_tool_call(facts, name, payload.get("arguments") or payload.get("input"))
        elif ptype in ("function_call_output", "custom_tool_call_output"):
            text = summarise_result(payload.get("output"))
            if looks_like_error(text):
                add_error(facts, calls.get(str(payload.get("call_id")), "?"), text)
        elif ptype == "message":
            text = codex_text(payload.get("content"))
            if payload.get("role") == "user":
                fallback.append((text, stamp))
            elif payload.get("role") == "assistant" and text:
                pass  # already counted via event_msg/agent_message

    if not saw_event_user:
        for text, stamp in fallback:
            add_user_message(facts, text, stamp)

    return facts


def codex_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for block in content:
            if isinstance(block, dict):
                out.append(str(block.get("text") or block.get("content") or ""))
            elif isinstance(block, str):
                out.append(block)
        return "\n".join(p for p in out if p)
    return ""


ERROR_HINTS = ("error", "traceback", "exception", "command failed", "no such file",
               "permission denied", "exit code 1", "exit status 1", "fatal:")


def looks_like_error(text: str) -> bool:
    low = text[:2000].lower()
    return any(h in low for h in ERROR_HINTS)


# --- plain text ------------------------------------------------------------------------

TEXT_TURN = re.compile(r"^\s*(?:#{1,6}\s*)?(user|assistant|用户|助手)\s*[:：]?\s*$", re.IGNORECASE)


def parse_text(path: Path) -> dict[str, Any]:
    """A markdown/plain transcript with 'user:' / 'assistant:' turn headers."""
    facts = blank_facts(path, "text")
    role, buffer = None, []

    def flush() -> None:
        if role and buffer:
            joined = "\n".join(buffer).strip()
            if role.lower() in ("user", "用户"):
                add_user_message(facts, joined, None)
            else:
                facts["counts"]["assistant_turns"] += 1

    for size, raw in iter_lines(path):
        if raw is None:
            facts["counts"]["oversized_lines"] += 1
            continue
        match = TEXT_TURN.match(raw)
        if match:
            flush()
            role, buffer = match.group(1), []
        else:
            buffer.append(raw.rstrip("\n"))
    flush()
    return facts


PARSERS = {"claude": parse_claude, "codex": parse_codex, "text": parse_text}


# --- discovery -------------------------------------------------------------------------

def discover(engine: str, claude_root: Path, codex_root: Path) -> list[tuple[Path, str]]:
    found: list[tuple[Path, str]] = []
    if engine in ("claude", "both") and claude_root.is_dir():
        found += [(p, "claude") for p in sorted(claude_root.glob("*/*.jsonl"))]
    if engine in ("codex", "both") and codex_root.is_dir():
        found += [(p, "codex") for p in sorted(codex_root.glob("*/*/*/*.jsonl"))]
    return found


def in_window(facts: dict[str, Any], since: datetime | None, until: datetime | None) -> bool:
    last, first = facts.get("last_seen"), facts.get("first_seen")
    if since and last and last < since.isoformat():
        return False
    if until and first and first > until.isoformat():
        return False
    return True


def too_old(path: Path, since: datetime | None) -> bool:
    """Cheap pre-filter: transcripts are append-only, so mtime >= the last line's time.

    An mtime before the window therefore proves the file has nothing in it, and we can skip
    the parse entirely.  A copy or rsync can only push mtime *forward*, which costs a
    needless parse rather than a wrong answer.
    """
    if since is None:
        return False
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < since
    except OSError:
        return False


def matches_project(path: Path, facts: dict[str, Any], needle: str | None) -> bool:
    """Match on path or recorded cwd.

    Both are needed.  Claude Code names its directories after a slugified cwd, which turns
    every non-ASCII character into a dash -- so a project called 接单工作台 lives in
    '-Users-example-Desktop------' and can only be found through the cwd recorded inside.
    """
    if not needle:
        return True
    low = needle.lower()
    return low in str(path).lower() or low in str(facts.get("cwd") or "").lower()


def ngrams(sequence: list[str], size: int) -> Iterable[tuple[str, ...]]:
    for i in range(len(sequence) - size + 1):
        yield tuple(sequence[i:i + size])


def aggregate(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    tools: Counter = Counter()
    shapes: Counter = Counter()
    seq: Counter = Counter()
    totals: Counter = Counter()
    for s in sessions:
        tools.update(s["tools"])
        shapes.update(s["command_shapes"])
        seq.update(ngrams(s["tool_sequence"], NGRAM_SIZE))
        totals.update(s["counts"])
        totals["bytes"] += s["bytes"]

    return {
        "sessions": len(sessions),
        "totals": dict(totals),
        "tools": dict(tools.most_common()),
        # Candidates for automation: a shape repeated this often was done by hand more than
        # once and is a Skill waiting to be written.  Judgement still belongs to the model.
        "repeated_commands": [
            {"shape": k, "times": v} for k, v in shapes.most_common(40) if v >= REPEAT_MIN
        ],
        "repeated_tool_sequences": [
            {"sequence": list(k), "times": v} for k, v in seq.most_common(25) if v >= REPEAT_MIN
        ],
        "corrections": sum(len(s["corrections"]) for s in sessions),
    }


def serialisable(facts: dict[str, Any], keep_text: bool) -> dict[str, Any]:
    out = dict(facts)
    out["tools"] = dict(facts["tools"].most_common())
    out["command_shapes"] = dict(facts["command_shapes"].most_common(30))
    out["tool_sequence_len"] = len(facts["tool_sequence"])
    out.pop("tool_sequence", None)
    if not keep_text:
        out["user_messages"] = [{"at": m["at"], "chars": len(m["text"])}
                                for m in facts["user_messages"]]
        out["corrections"] = [{"at": m["at"], "chars": len(m["text"])}
                              for m in facts["corrections"]]
        out["errors"] = [{"tool": e["tool"]} for e in facts["errors"]]
    return out


def render_text(report: dict[str, Any]) -> str:
    agg = report["summary"]
    win = report["window"]
    lines = [
        "TRANSCRIPT FACTS",
        f"  window       {win['since'] or '-'} .. {win['until'] or 'now'}",
        f"  project      {win.get('project') or 'all'}",
        f"  sessions     {agg['sessions']}"
        f"   (of {win.get('candidates', 0)} files;"
        f" {win.get('skipped_by_mtime', 0)} skipped by mtime)",
        f"  user turns   {agg['totals'].get('user_turns', 0)}",
        f"  assistant    {agg['totals'].get('assistant_turns', 0)}",
        f"  tool calls   {agg['totals'].get('tool_calls', 0)}"
        f"   (errors {agg['totals'].get('tool_errors', 0)})",
        f"  corrections  {agg['corrections']}   <- candidates, model must judge each",
        f"  bytes        {agg['totals'].get('bytes', 0):,}",
        f"  skipped      {agg['totals'].get('oversized_lines', 0)} oversized,"
        f" {agg['totals'].get('unparsable_lines', 0)} unparsable",
    ]
    if agg["repeated_commands"]:
        lines.append("\nREPEATED COMMANDS  (automation candidates)")
        for item in agg["repeated_commands"][:15]:
            lines.append(f"  {item['times']:4}x  {item['shape']}")
    if agg["repeated_tool_sequences"]:
        lines.append("\nREPEATED TOOL SEQUENCES")
        for item in agg["repeated_tool_sequences"][:10]:
            lines.append(f"  {item['times']:4}x  {' -> '.join(item['sequence'])}")
    if agg["tools"]:
        lines.append("\nTOOLS")
        for name, count in list(agg["tools"].items())[:15]:
            lines.append(f"  {count:5}  {name}")
    lines.append("\nNumbers above are mechanical. Interpretation is the model's job;"
                 " estimating these by eye is a failed retrospective.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path, help="transcript files to read")
    parser.add_argument("--engine", choices=("claude", "codex", "both", "text"))
    parser.add_argument("--since", help="ISO timestamp or 7d / 36h / 90m")
    parser.add_argument("--until", help="ISO timestamp")
    parser.add_argument("--project", help="only sessions whose path or cwd contains this")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--out", type=Path, help="also write the full JSON here")
    parser.add_argument("--no-text", action="store_true",
                        help="omit message/error bodies; metadata may remain sensitive")
    parser.add_argument("--claude-root", type=Path,
                        default=Path(os.getenv("CLAUDE_PROJECTS", CLAUDE_ROOT)))
    parser.add_argument("--codex-root", type=Path,
                        default=Path(os.getenv("CODEX_SESSIONS", CODEX_ROOT)))
    args = parser.parse_args(argv)

    if not args.paths and not args.engine:
        parser.error("give transcript paths, or --engine claude|codex|both")

    since, until = parse_when(args.since), parse_when(args.until)
    targets: list[tuple[Path, str]] = []
    if args.engine and args.engine != "text":
        targets += discover(args.engine, args.claude_root, args.codex_root)
    for path in args.paths:
        engine = args.engine if args.engine in PARSERS else guess_engine(path)
        targets.append((path, engine))
    sessions: list[dict[str, Any]] = []
    skipped_old = 0
    for path, engine in targets:
        if not path.is_file():
            print(f"skip (missing): {path}", file=sys.stderr)
            continue
        if too_old(path, since):
            skipped_old += 1
            continue
        try:
            facts = PARSERS[engine](path)
        except OSError as exc:
            print(f"skip ({exc}): {path}", file=sys.stderr)
            continue
        if not in_window(facts, since, until):
            continue
        if not matches_project(path, facts, args.project):
            continue
        sessions.append(facts)

    sessions.sort(key=lambda s: s["last_seen"] or "")
    report = {
        "window": {"since": since.isoformat() if since else None,
                   "until": until.isoformat() if until else None,
                   "candidates": len(targets), "skipped_by_mtime": skipped_old,
                   "project": args.project},
        "summary": aggregate(sessions),
        "sessions": [serialisable(s, not args.no_text) for s in sessions],
    }

    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json"
          else render_text(report))
    return 0


def guess_engine(path: Path) -> str:
    text = str(path)
    if ".codex" in text or path.name.startswith("rollout-"):
        return "codex"
    if ".claude" in text or path.suffix == ".jsonl":
        return "claude"
    return "text"


if __name__ == "__main__":
    raise SystemExit(main())
