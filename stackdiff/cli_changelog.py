"""CLI sub-command: generate a changelog entry from two Compose files."""

from __future__ import annotations

import argparse
import sys

from stackdiff.pipeline import run_pipeline
from stackdiff.filter import FilterOptions
from stackdiff.changelog import build_changelog_entry, render_changelog


def build_changelog_parser(subparsers: argparse.Action) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "changelog",
        help="Print a Markdown changelog entry for the diff between two Compose files.",
    )
    p.add_argument("base", help="Base Compose file")
    p.add_argument("head", help="Head Compose file")
    p.add_argument(
        "--version",
        default="unreleased",
        help="Version label for the changelog entry (default: unreleased)",
    )
    p.add_argument(
        "--timestamp",
        default=None,
        help="ISO-8601 timestamp to embed (default: current UTC time)",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when changes are present",
    )
    return p


def run_changelog(args: argparse.Namespace) -> int:
    """Execute the changelog sub-command."""
    result = run_pipeline(
        base_path=args.base,
        head_path=args.head,
        filter_opts=FilterOptions(),
    )
    if result.warnings:
        for w in result.warnings:
            print(f"warning: {w}", file=sys.stderr)

    entry = build_changelog_entry(
        report=result.report,
        version=args.version,
        timestamp=args.timestamp,
    )
    print(render_changelog(entry))

    if args.exit_code and not entry.is_empty():
        return 1
    return 0
