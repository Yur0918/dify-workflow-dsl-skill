#!/usr/bin/env python3
"""Render a compact Mermaid flowchart from a Dify DSL YAML export."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


def compact(value: object, limit: int = 60) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[: limit - 1] + "..." if len(text) > limit else text


def escape_label(value: object) -> str:
    text = compact(value).replace('"', "'").replace("[", "(").replace("]", ")")
    return text.replace("&", "and")


def mermaid_id(value: object) -> str:
    return "n" + re.sub(r"[^A-Za-z0-9_]", "_", str(value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Dify DSL graph as Mermaid.")
    parser.add_argument("dsl", type=Path, help="Dify DSL YAML file")
    parser.add_argument("--output", type=Path, help="Write Mermaid to this file instead of stdout")
    args = parser.parse_args()

    try:
        data = yaml.safe_load(args.dsl.read_text(encoding="utf-8-sig"))
        graph = data["workflow"]["graph"]
        nodes = graph["nodes"]
        edges = graph["edges"]
    except (OSError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f"Unable to read Dify graph: {exc}", file=sys.stderr)
        return 1

    known = {str(node.get("id")): node for node in nodes if node.get("id") is not None}
    lines = ["flowchart LR"]
    for node_id, node in known.items():
        node_data = node.get("data") or {}
        title = node_data.get("title") or node_data.get("type") or node.get("type") or node_id
        kind = node_data.get("type") or node.get("type") or "node"
        lines.append(f'  {mermaid_id(node_id)}["{escape_label(title)} ({escape_label(kind)})"]')

    for edge in edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        if source not in known or target not in known:
            continue
        source_id = mermaid_id(source)
        target_id = mermaid_id(target)
        handle = compact(edge.get("sourceHandle"), 30)
        if handle and handle not in {"source", "default"}:
            lines.append(f'  {source_id} -->|"{escape_label(handle)}"| {target_id}')
        else:
            lines.append(f"  {source_id} --> {target_id}")

    output = "\n".join(lines) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
