"""CLI sub-command: profile

Prints a complexity profile for each changed service in a diff.
Intended to be wired into the main CLI as a sub-command.
"""
from __future__ import annotations

import argparse
import sys
from typing import List

from stackdiff.pipeline import run_pipeline
from stackdiff.filter import FilterOptions
from stackdiff.profiler import ProfileReport, profile_report


_BAR_CHAR = "█"
_BAR_MAX_WIDTH = 20


def _render_bar(score: int, max_score: int) -> str:
    if max_score == 0:
        return ""
    filled = round((score / max_score) * _BAR_MAX_WIDTH)
    return _BAR_CHAR * filled


def render_profile(pr: ProfileReport, *, use_color: bool = True) -> List[str]:
    """Return a list of human-readable lines for the profile report."""
    if not pr.profiles:
        return ["No service changes to profile."]

    max_score = max(p.complexity_score for p in pr.profiles)
    lines: List[str] = []
    header = f"{'Service':<30} {'Score':>6}  {'Breakdown':<25}  Bar"
    lines.append(header)
    lines.append("-" * len(header))

    for p in pr.profiles:
        breakdown = f"+{p.added_fields} ~{p.changed_fields} -{p.removed_fields}"
        bar = _render_bar(p.complexity_score, max_score)
        lines.append(f"{p.service_name:<30} {p.complexity_score:>6}  {breakdown:<25}  {bar}")

    if pr.most_complex:
        lines.append("")
        lines.append(f"Most complex service: {pr.most_complex.service_name}")

    return lines


def build_profile_parser(subparsers) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "profile",
        help="Show per-service complexity scores for a diff.",
    )
    p.add_argument("file_a", help="First Compose file")
    p.add_argument("file_b", help="Second Compose file")
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    return p


def run_profile(args: argparse.Namespace) -> int:
    """Entry point for the profile sub-command. Returns an exit code."""
    options = FilterOptions()
    result = run_pipeline(args.file_a, args.file_b, filter_options=options)

    if result.warnings:
        for w in result.warnings:
            print(f"[warn] {w}", file=sys.stderr)

    pr = profile_report(result.report)
    lines = render_profile(pr, use_color=not args.no_color)
    print("\n".join(lines))
    return 0
