"""CLI sub-command: tag — prints semantic tags for each changed service."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.pipeline import run_pipeline
from stackdiff.tagger import tag_report


def build_tagger_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:
    p = sub.add_parser(
        "tag",
        help="Show semantic tags for each changed service.",
    )
    p.add_argument("base", help="Base Docker Compose file.")
    p.add_argument("head", help="Head Docker Compose file.")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--filter-tag",
        dest="filter_tag",
        default=None,
        metavar="TAG",
        help="Only show services that have this tag.",
    )
    return p


def run_tagger(args: argparse.Namespace) -> int:
    result = run_pipeline(args.base, args.head)
    tr = tag_report(result.report)

    services = tr.services
    if args.filter_tag:
        services = [s for s in services if args.filter_tag in s.tags]

    if args.format == "json":
        print(json.dumps({"services": [s.to_dict() for s in services]}, indent=2))
        return 0

    if not services:
        print("No tagged changes found.")
        return 0

    for svc in services:
        tags_str = ", ".join(sorted(svc.tags))
        print(f"  {svc.name}: {tags_str}")

    return 0


if __name__ == "__main__":
    import argparse as _ap

    _parser = _ap.ArgumentParser()
    _subs = _parser.add_subparsers(dest="command")
    build_tagger_parser(_subs)
    _args = _parser.parse_args()
    sys.exit(run_tagger(_args))
