"""Sort the entries inside a DiffReport for deterministic output."""

from __future__ import annotations

from stackdiff.reporter import DiffReport


def sort_report(report: DiffReport) -> DiffReport:
    """Return a new DiffReport with all collections sorted alphabetically."""
    return DiffReport(
        added=sorted(report.added),
        removed=sorted(report.removed),
        changed=dict(sorted(report.changed.items())),
    )
