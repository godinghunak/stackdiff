"""Produces a human-readable plain-text summary of a DiffReport."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from stackdiff.reporter import DiffReport


@dataclass
class SummaryLine:
    """A single line in the summary output."""

    category: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    text: str


def _pluralise(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


def summarize_report(report: DiffReport) -> List[SummaryLine]:
    """Return a list of SummaryLines describing the diff at a high level."""
    lines: List[SummaryLine] = []

    added = report.added
    removed = report.removed
    changed = report.changed

    total_services = len(added) + len(removed) + len(changed)

    if total_services == 0:
        lines.append(SummaryLine("unchanged", "No service-level changes detected."))
        return lines

    lines.append(
        SummaryLine(
            "unchanged",
            f"{total_services} {_pluralise(total_services, 'service', 'services')} affected.",
        )
    )

    if added:
        names = ", ".join(sorted(added))
        lines.append(
            SummaryLine(
                "added",
                f"Added ({len(added)}): {names}",
            )
        )

    if removed:
        names = ", ".join(sorted(removed))
        lines.append(
            SummaryLine(
                "removed",
                f"Removed ({len(removed)}): {names}",
            )
        )

    if changed:
        for name, diff in sorted(changed.items()):
            field_count = len(diff.changes)
            lines.append(
                SummaryLine(
                    "changed",
                    f"Changed '{name}': {field_count} {_pluralise(field_count, 'field', 'fields')} modified "
                    f"({', '.join(sorted(diff.changes.keys()))})",
                )
            )

    return lines


def render_summary(report: DiffReport) -> str:
    """Render the summary as a newline-joined string."""
    return "\n".join(line.text for line in summarize_report(report))
