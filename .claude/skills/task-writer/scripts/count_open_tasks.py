#!/usr/bin/env python3
"""Count open kanban tickets per assignee.

Scans every `.md` task file under the DevPath kanban tree:
  - docs/project-management/ticket/backlog/
  - docs/project-management/ticket/sprint-*/todo/
  - docs/project-management/ticket/sprint-*/in-progress/
  - docs/project-management/ticket/sprint-*/in-review/

Tickets in `done/` are excluded — those are closed.

Status is derived from the parent folder name; the `Status:` metadata line is ignored
(folder is the source of truth, per CLAUDE.md). Assignee is read from the first
`- Assignee: <name>` line.

Output: JSON to stdout, e.g.
    {"Phuc Pham": 3, "Long Nguyen": 1, "_unassigned": 2}

Usage:
    python .claude/skills/task-writer/scripts/count_open_tasks.py
    python .claude/skills/task-writer/scripts/count_open_tasks.py --root /path/to/repo
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

OPEN_FOLDERS = {"backlog", "todo", "in-progress", "in-review"}
UNASSIGNED_KEY = "_unassigned"
UNASSIGNED_MARKERS = {"", "—", "-", "tbd", "n/a", "none"}

ASSIGNEE_RE = re.compile(r"^\s*[-*]?\s*\**Assignee\**\s*:\s*(.*?)\s*$", re.IGNORECASE)


def read_assignee(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        m = ASSIGNEE_RE.match(line)
        if not m:
            continue
        val = re.sub(r"^[*_`]+|[*_`]+$", "", m.group(1).strip()).strip()
        return val
    return None


def normalize(raw: str | None) -> str:
    if raw is None:
        return UNASSIGNED_KEY
    cleaned = raw.strip()
    if cleaned.lower() in UNASSIGNED_MARKERS:
        return UNASSIGNED_KEY
    return cleaned


def collect(root: Path) -> Counter:
    counts: Counter = Counter()
    ticket_root = root / "docs" / "project-management" / "ticket"
    if not ticket_root.is_dir():
        return counts
    for path in ticket_root.rglob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        # parent folder name must be one of the open kanban states
        if path.parent.name not in OPEN_FOLDERS:
            continue
        counts[normalize(read_assignee(path))] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repo root (defaults to current working directory).",
    )
    args = parser.parse_args()
    if not args.root.is_dir():
        print(f"error: root not found: {args.root}", file=sys.stderr)
        return 1
    counts = collect(args.root.resolve())
    print(json.dumps(dict(sorted(counts.items())), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
