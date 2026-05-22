"""Formats ServiceDiff results into human-readable output."""

from dataclasses import fields
from typing import List

from stackdiff.differ import ServiceDiff

ADD_SYMBOL = "+"
REMOVE_SYMBOL = "-"
CHANGE_SYMBOL = "~"
SEPARATOR = "-" * 60


def _format_added(names: List[str]) -> List[str]:
    return [f"  {ADD_SYMBOL} {name}" for name in sorted(names)]


def _format_removed(names: List[str]) -> List[str]:
    return [f"  {REMOVE_SYMBOL} {name}" for name in sorted(names)]


def _format_changed(diff: ServiceDiff) -> List[str]:
    lines = []
    for service_name, changes in sorted(diff.changed.items()):
        lines.append(f"  {CHANGE_SYMBOL} {service_name}")
        for key, (old_val, new_val) in sorted(changes.items()):
            lines.append(f"      {key}: {old_val!r} -> {new_val!r}")
    return lines


def format_diff(diff: ServiceDiff, color: bool = False) -> str:
    """Return a formatted string summarising the diff.

    Args:
        diff: A ServiceDiff produced by diff_services.
        color: If True, apply ANSI colour codes.

    Returns:
        Multi-line string ready to print.
    """
    lines = [SEPARATOR, "stackdiff — service-level diff summary", SEPARATOR]

    if diff.added:
        lines.append("Added services:")
        lines.extend(_format_added(list(diff.added)))

    if diff.removed:
        lines.append("Removed services:")
        lines.extend(_format_removed(list(diff.removed)))

    if diff.changed:
        lines.append("Changed services:")
        lines.extend(_format_changed(diff))

    if not diff.added and not diff.removed and not diff.changed:
        lines.append("No differences found.")

    lines.append(SEPARATOR)
    output = "\n".join(lines)

    if color:
        output = _apply_color(output)

    return output


def _apply_color(text: str) -> str:
    """Apply basic ANSI colour codes to diff symbols."""
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

    result = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(ADD_SYMBOL + " "):
            line = GREEN + line + RESET
        elif stripped.startswith(REMOVE_SYMBOL + " "):
            line = RED + line + RESET
        elif stripped.startswith(CHANGE_SYMBOL + " "):
            line = YELLOW + line + RESET
        result.append(line)
    return "\n".join(result)
