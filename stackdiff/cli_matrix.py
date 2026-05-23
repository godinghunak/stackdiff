"""CLI sub-command: render a change matrix for two Compose files."""
from __future__ import annotations

import argparse
import sys
from typing import List

from stackdiff.pipeline import run_pipeline
from stackdiff.differ_matrix import build_matrix, ChangeMatrix

_CHANGE_SYMBOLS = {
    "added": "+",
    "removed": "-",
    "changed": "~",
    "unchanged": "=",
}


def render_matrix(matrix: ChangeMatrix) -> List[str]:
    """Return human-readable lines for the change matrix."""
    if not matrix.cells:
        return ["No services found in either file."]

    width = max(len(c.service) for c in matrix.cells)
    lines = [f"  {'SERVICE':<{width}}  TYPE"]
    lines.append("  " + "-" * (width + 10))
    for cell in matrix.cells:
        symbol = _CHANGE_SYMBOLS.get(cell.change_type, "?")
        lines.append(f"  {cell.service:<{width}}  {symbol}  {cell.change_type}")

    summary = matrix.to_dict()["summary"]
    lines.append("")
    lines.append(
        f"  added={summary['added']}  removed={summary['removed']}  "
        f"changed={summary['changed']}  unchanged={summary['unchanged']}"
    )
    return lines


def build_matrix_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser("matrix", help="Show a change matrix across services")
    p.add_argument("file_a", help="First Compose file")
    p.add_argument("file_b", help="Second Compose file")
    return p


def run_matrix(args: argparse.Namespace) -> int:
    result = run_pipeline(args.file_a, args.file_b)
    matrix = build_matrix(result.report)
    for line in render_matrix(matrix):
        print(line)
    return 0
