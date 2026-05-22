"""Command-line interface for stackdiff."""

import argparse
import sys

from stackdiff.parser import ComposeParseError, load_compose_file, extract_services
from stackdiff.differ import diff_services
from stackdiff.formatter import format_diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff",
        description="Compare two Docker Compose files and summarise service-level changes.",
    )
    parser.add_argument("base", help="Path to the base Docker Compose file.")
    parser.add_argument("target", help="Path to the target Docker Compose file.")
    parser.add_argument(
        "--color",
        action="store_true",
        default=False,
        help="Enable coloured output.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found.",
    )
    return parser


def run(argv=None) -> int:
    """Entry point for the CLI.

    Returns:
        Exit code (0 = no diff or success, 1 = diff found when --exit-code set, 2 = error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        base_data = load_compose_file(args.base)
        target_data = load_compose_file(args.target)
    except ComposeParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    base_services = extract_services(base_data)
    target_services = extract_services(target_data)

    diff = diff_services(base_services, target_services)
    print(format_diff(diff, color=args.color))

    has_diff = bool(diff.added or diff.removed or diff.changed)
    if args.exit_code and has_diff:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
