"""CLI sub-commands for snapshot management: save and compare."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stackdiff.pipeline import run_pipeline
from stackdiff.snapshotter import save_snapshot, SnapshotError
from stackdiff.snapshot_compare import compare_against_snapshot


def build_snapshot_parser(parent: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'snapshot' sub-commands onto *parent*."""
    snap_parser = parent.add_parser("snapshot", help="Manage diff snapshots")
    sub = snap_parser.add_subparsers(dest="snap_cmd", required=True)

    # save
    save_p = sub.add_parser("save", help="Save current diff as a snapshot")
    save_p.add_argument("file_a", help="First Compose file")
    save_p.add_argument("file_b", help="Second Compose file")
    save_p.add_argument("output", help="Destination snapshot JSON file")

    # compare
    cmp_p = sub.add_parser("compare", help="Compare current diff against a snapshot")
    cmp_p.add_argument("file_a", help="First Compose file")
    cmp_p.add_argument("file_b", help="Second Compose file")
    cmp_p.add_argument("snapshot", help="Baseline snapshot JSON file")
    cmp_p.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit with code 1 when new regressions are detected",
    )


def run_snapshot(args: argparse.Namespace) -> int:
    """Dispatch snapshot sub-command; return exit code."""
    result = run_pipeline(Path(args.file_a), Path(args.file_b))
    if result.validation.warnings:
        for w in result.validation.warnings:
            print(f"warning: {w}", file=sys.stderr)

    if args.snap_cmd == "save":
        try:
            snap = save_snapshot(result.report, Path(args.output))
            print(f"Snapshot saved to {snap.path}")
        except SnapshotError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.snap_cmd == "compare":
        comparison, warning = compare_against_snapshot(
            result.report, Path(args.snapshot)
        )
        if warning:
            print(f"warning: {warning}", file=sys.stderr)

        import json
        print(json.dumps(comparison.to_dict(), indent=2))

        if args.fail_on_regression and comparison.has_regressions:
            return 1
        return 0

    return 0
