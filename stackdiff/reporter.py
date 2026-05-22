"""Generates a structured report dict from a diff result set."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from stackdiff.differ import ServiceDiff


@dataclass
class DiffReport:
    added: list[str]
    removed: list[str]
    changed: list[dict[str, Any]]
    unchanged: list[str]
    summary: dict[str, int]

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_report(diffs: dict[str, ServiceDiff]) -> DiffReport:
    """Convert a mapping of service name -> ServiceDiff into a DiffReport."""
    added: list[str] = []
    removed: list[str] = []
    changed: list[dict[str, Any]] = []
    unchanged: list[str] = []

    for name, diff in diffs.items():
        if diff.added:
            added.append(name)
        elif diff.removed:
            removed.append(name)
        elif diff.changes:
            changed.append({"service": name, "changes": diff.changes})
        else:
            unchanged.append(name)

    summary = {
        "added": len(added),
        "removed": len(removed),
        "changed": len(changed),
        "unchanged": len(unchanged),
        "total": len(diffs),
    }

    return DiffReport(
        added=sorted(added),
        removed=sorted(removed),
        changed=sorted(changed, key=lambda x: x["service"]),
        unchanged=sorted(unchanged),
        summary=summary,
    )
