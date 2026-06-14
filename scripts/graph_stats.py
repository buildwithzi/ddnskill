#!/usr/bin/env python3
"""Inspect a CONTENT_GRAPH.md file.

Usage:
    python scripts/graph_stats.py CONTENT_GRAPH.md

The parser is intentionally simple and expects node blocks in this form:

    ## NODE P1.2
    - Parent: P1
    - Relation: WHY
    - Depth: 2
    - Evidence: E2
    - Status: CANDIDATE

It prints JSON and uses only Python's standard library.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

NODE_RE = re.compile(r"^#{2,6}\s+NODE\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+([^:]+):\s*(.*)$")


def parse_graph(path: Path) -> List[Dict[str, str]]:
    nodes: List[Dict[str, str]] = []
    current: Dict[str, str] | None = None

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        match = NODE_RE.match(line)
        if match:
            if current is not None:
                nodes.append(current)
            current = {"id": match.group(1).strip()}
            continue

        if current is None:
            continue

        field = FIELD_RE.match(line)
        if field:
            key = field.group(1).strip().lower().replace(" ", "_")
            current[key] = field.group(2).strip()

    if current is not None:
        nodes.append(current)
    return nodes


def to_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python graph_stats.py CONTENT_GRAPH.md", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    nodes = parse_graph(path)
    ids = {node.get("id", "") for node in nodes}
    children: Dict[str, List[str]] = defaultdict(list)
    orphan_nodes: List[str] = []
    duplicate_ids = [node_id for node_id, count in Counter(node.get("id", "") for node in nodes).items() if count > 1]

    for node in nodes:
        node_id = node.get("id", "")
        parent = node.get("parent", "")
        if parent and parent != "NONE":
            children[parent].append(node_id)
            if parent not in ids:
                orphan_nodes.append(node_id)

    depths = [depth for node in nodes if (depth := to_int(node.get("depth"))) is not None]
    status_counts = Counter(node.get("status", "UNKNOWN") for node in nodes)
    evidence_counts = Counter(node.get("evidence", "UNKNOWN") for node in nodes)
    relation_counts = Counter(node.get("relation", "UNKNOWN") for node in nodes)
    type_counts = Counter(node.get("type", "UNKNOWN") for node in nodes)

    leaf_nodes = [node.get("id", "") for node in nodes if not children.get(node.get("id", ""))]
    expandable_without_hint = [
        node.get("id", "")
        for node in nodes
        if node.get("status") not in {"REJECTED", "EXHAUSTED"}
        and not node.get("next_expansion")
    ]

    output = {
        "file": str(path),
        "node_count": len(nodes),
        "max_depth": max(depths) if depths else None,
        "leaf_count": len(leaf_nodes),
        "status_counts": dict(status_counts),
        "evidence_counts": dict(evidence_counts),
        "relation_counts": dict(relation_counts),
        "type_counts": dict(type_counts),
        "duplicate_ids": duplicate_ids,
        "orphan_nodes": orphan_nodes,
        "nodes_without_next_expansion_hint": expandable_without_hint,
        "notes": [
            "Leaf nodes are not automatically publishable; inspect their content and evidence.",
            "An orphan node references a parent ID not found in the file.",
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
