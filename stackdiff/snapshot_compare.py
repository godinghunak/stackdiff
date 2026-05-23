"""Compare a live DiffReport against a stored snapshot."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from stackdiff.reporter import DiffReport
from stackdiff.snapshotter import load_snapshot, SnapshotError


@dataclass
class SnapshotComparison:
    """Result of comparing a current report against a baseline snapshot."""

    new_additions: set[str] = field(default_factory=set)
    new_removals: set[str] = field(default_factory=set)
    resolved_additions: set[str] = field(default_factory=set)
    resolved_removals: set[str] = field(default_factory=set)
    new_changed: set[str] = field(default_factory=set)
    resolved_changed: set[str] = field(default_factory=set)

    @property
    def has_regressions(self) -> bool:
        return bool(self.new_additions or self.new_removals or self.new_changed)

    def to_dict(self) -> dict:
        return {
            "new_additions": sorted(self.new_additions),
            "new_removals": sorted(self.new_removals),
            "resolved_additions": sorted(self.resolved_additions),
            "resolved_removals": sorted(self.resolved_removals),
            "new_changed": sorted(self.new_changed),
            "resolved_changed": sorted(self.resolved_changed),
            "has_regressions": self.has_regressions,
        }


def compare_against_snapshot(
    current: DiffReport, snapshot_path: Path
) -> tuple[SnapshotComparison, Optional[str]]:
    """Compare *current* against the snapshot at *snapshot_path*.

    Returns ``(comparison, warning)`` where *warning* is a non-fatal message
    string when the snapshot is missing or unreadable, or ``None`` on success.
    """
    try:
        baseline = load_snapshot(snapshot_path)
    except SnapshotError as exc:
        empty = DiffReport(added=set(), removed=set(), changed={})
        return _compare(current, empty), str(exc)

    return _compare(current, baseline), None


def _compare(current: DiffReport, baseline: DiffReport) -> SnapshotComparison:
    return SnapshotComparison(
        new_additions=current.added - baseline.added,
        new_removals=current.removed - baseline.removed,
        resolved_additions=baseline.added - current.added,
        resolved_removals=baseline.removed - current.removed,
        new_changed=set(current.changed) - set(baseline.changed),
        resolved_changed=set(baseline.changed) - set(current.changed),
    )
