"""Snapshot support: save and load DiffReport snapshots to/from JSON files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from stackdiff.reporter import DiffReport, build_report
from stackdiff.differ import ServiceDiff


class SnapshotError(Exception):
    """Raised when a snapshot cannot be saved or loaded."""


@dataclass
class Snapshot:
    path: Path
    report: DiffReport

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "added": list(self.report.added),
            "removed": list(self.report.removed),
            "changed": {
                name: {
                    "added_keys": list(diff.added_keys),
                    "removed_keys": list(diff.removed_keys),
                    "changed_keys": list(diff.changed_keys),
                }
                for name, diff in self.report.changed.items()
            },
        }


def save_snapshot(report: DiffReport, path: Path) -> Snapshot:
    """Persist a DiffReport as a JSON snapshot file."""
    snapshot = Snapshot(path=path, report=report)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
    except OSError as exc:
        raise SnapshotError(f"Cannot write snapshot to {path}: {exc}") from exc
    return snapshot


def load_snapshot(path: Path) -> DiffReport:
    """Load a DiffReport from a previously saved JSON snapshot file."""
    if not path.exists():
        raise SnapshotError(f"Snapshot file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Cannot read snapshot from {path}: {exc}") from exc

    changed: dict[str, ServiceDiff] = {}
    for name, diff_data in data.get("changed", {}).items():
        changed[name] = ServiceDiff(
            name=name,
            added_keys=set(diff_data.get("added_keys", [])),
            removed_keys=set(diff_data.get("removed_keys", [])),
            changed_keys=set(diff_data.get("changed_keys", [])),
        )

    return DiffReport(
        added=set(data.get("added", [])),
        removed=set(data.get("removed", [])),
        changed=changed,
    )
