"""Compute numeric statistics from a DiffReport."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stackdiff.reporter import DiffReport


@dataclass(frozen=True)
class DiffStats:
    """Aggregated counts derived from a :class:`DiffReport`."""

    total_services: int
    added: int
    removed: int
    changed: int
    unchanged: int

    @property
    def change_rate(self) -> float:
        """Fraction of services that have any change (0.0 – 1.0)."""
        if self.total_services == 0:
            return 0.0
        return (self.added + self.removed + self.changed) / self.total_services

    def to_dict(self) -> dict[str, object]:
        return {
            "total_services": self.total_services,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "unchanged": self.unchanged,
            "change_rate": round(self.change_rate, 4),
        }


def compute_stats(report: "DiffReport") -> DiffStats:
    """Return a :class:`DiffStats` instance for *report*."""
    added = len(report.added)
    removed = len(report.removed)
    changed = len(report.changed)
    unchanged = len(report.unchanged)
    total = added + removed + changed + unchanged
    return DiffStats(
        total_services=total,
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
    )
