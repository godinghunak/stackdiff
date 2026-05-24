"""CLI sub-command: stackdiff heatmap — render a change-intensity heatmap."""
from __future__ import annotations

import argparse
import sys

from stackdiff.pipeline import run_pipeline
from stackdiff.filter import FilterOptions
from stackdiff.differ_heatmap import build_heatmap, DiffHeatmap

_BAR_CHAR = "█"
_MAX_BAR = 20


def _render_bar(count: int, max_count: int) -> str:
    if max_count == 0:
        return ""
    filled = round((count / max_count) * _MAX_BAR)
    return _BAR_CHAR * filled


def render_heatmap(heatmap: DiffHeatmap) -> str:
    if not heatmap.entries:
        return "No changes detected — heatmap is empty."

    max_count = heatmap.entries[0].change_count  # already sorted descending
    lines = ["Change Heatmap", "=" * 40]
    for entry in heatmap.entries:
        bar = _render_bar(entry.change_count, max_count)
        types = ", ".join(entry.change_types)
        lines.append(f"  {entry.service:<25} {bar:<20} {entry.change_count:>3}  [{types}]")
    return "\n".join(lines)


def build_heatmap_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("heatmap", help="Show a change-intensity heatmap")
    p.add_argument("file_a", help="First Compose file")
    p.add_argument("file_b", help="Second Compose file")
    p.add_argument("--only", nargs="+", metavar="SERVICE", default=None,
                   help="Restrict heatmap to these services")
    p.set_defaults(func=run_heatmap)


def run_heatmap(args: argparse.Namespace) -> int:
    opts = FilterOptions(include_services=args.only or [])
    result = run_pipeline(args.file_a, args.file_b, filter_options=opts)

    if result.validation.warnings:
        for w in result.validation.warnings:
            print(f"[warn] {w}", file=sys.stderr)

    heatmap = build_heatmap(result.report)
    print(render_heatmap(heatmap))
    return 0
