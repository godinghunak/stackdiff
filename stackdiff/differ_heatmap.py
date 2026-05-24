"""Heatmap: ranks services by number of changed fields across a diff report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from stackdiff.reporter import DiffReport
from stackdiff.differ import ServiceDiff


@dataclass
class HeatmapEntry:
    service: str
    change_count: int
    change_types: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "change_count": self.change_count,
            "change_types": sorted(self.change_types),
        }


@dataclass
class DiffHeatmap:
    entries: List[HeatmapEntry] = field(default_factory=list)

    def hottest(self) -> HeatmapEntry | None:
        """Return the service with the most changes, or None if empty."""
        return max(self.entries, key=lambda e: e.change_count, default=None)

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}


def _count_changes(diff: ServiceDiff) -> tuple[int, List[str]]:
    """Return (total_change_count, list_of_change_type_labels) for a diff."""
    types: List[str] = []
    count = 0

    if diff.added:
        types.append("added")
        count += len(diff.added)
    if diff.removed:
        types.append("removed")
        count += len(diff.removed)
    if diff.changed:
        types.append("changed")
        count += len(diff.changed)

    return count, types


def build_heatmap(report: DiffReport) -> DiffHeatmap:
    """Build a heatmap from *all* services that have at least one change."""
    entries: List[HeatmapEntry] = []

    for service, diff in report.changes.items():
        count, types = _count_changes(diff)
        if count > 0:
            entries.append(HeatmapEntry(service=service, change_count=count, change_types=types))

    # Sort descending by change_count, then alphabetically for stability
    entries.sort(key=lambda e: (-e.change_count, e.service))
    return DiffHeatmap(entries=entries)
