"""CLI sub-command: render a dependency graph for a diff."""
from __future__ import annotations

import argparse
from typing import Dict

from stackdiff.differ_graph import DiffGraph, build_graph
from stackdiff.pipeline import run_pipeline

_CHANGE_SYMBOLS: Dict[str, str] = {
    "added": "[+]",
    "removed": "[-]",
    "changed": "[~]",
    "unchanged": "[ ]",
}


def render_graph(graph: DiffGraph, *, color: bool = False) -> str:
    lines = []
    for name in graph.all_service_names():
        node = graph.nodes[name]
        symbol = _CHANGE_SYMBOLS.get(node.change_type, "[ ]")
        line = f"{symbol} {name}"
        if node.depends_on:
            line += " -> " + ", ".join(node.depends_on)
        affected = graph.affected_by(name)
        if affected:
            line += f"  (needed by: {', '.join(sorted(affected))})"
        lines.append(line)
    return "\n".join(lines) if lines else "(no services)"


def build_graph_parser(subparsers: argparse.Action) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "graph",
        help="Show service dependency graph with change annotations",
    )
    p.add_argument("file_a", help="First compose file")
    p.add_argument("file_b", help="Second compose file")
    p.add_argument("--no-color", action="store_true", help="Disable colour output")
    return p


def run_graph(args: argparse.Namespace) -> int:
    result = run_pipeline(args.file_a, args.file_b)
    if result.validation and not result.validation.is_clean():
        for w in result.validation.warnings:
            print(f"WARNING: {w}")

    # Merge raw services from both compose data sets
    raw: Dict[str, dict] = {}
    for svc_map in (result.services_a, result.services_b):
        for name, defn in svc_map.items():
            raw.setdefault(name, defn)

    graph = build_graph(result.report, raw)
    print(render_graph(graph, color=not args.no_color))
    return 0
