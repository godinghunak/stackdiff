"""Builds a cross-service change matrix from a DiffReport."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from stackdiff.reporter import DiffReport


@dataclass
class MatrixCell:
    """A single cell in the change matrix representing one service's change type."""

    service: str
    change_type: str  # 'added' | 'removed' | 'changed' | 'unchanged'

    def to_dict(self) -> dict:
        return {"service": self.service, "change_type": self.change_type}


@dataclass
class ChangeMatrix:
    """A flat matrix of all services and their change categories."""

    cells: List[MatrixCell] = field(default_factory=list)

    def services_by_type(self, change_type: str) -> List[str]:
        """Return service names matching a given change type."""
        return [c.service for c in self.cells if c.change_type == change_type]

    def to_dict(self) -> dict:
        return {
            "cells": [c.to_dict() for c in self.cells],
            "summary": {
                "added": len(self.services_by_type("added")),
                "removed": len(self.services_by_type("removed")),
                "changed": len(self.services_by_type("changed")),
                "unchanged": len(self.services_by_type("unchanged")),
            },
        }


def build_matrix(report: DiffReport) -> ChangeMatrix:
    """Construct a ChangeMatrix from a DiffReport."""
    cells: List[MatrixCell] = []

    for name in report.added:
        cells.append(MatrixCell(service=name, change_type="added"))

    for name in report.removed:
        cells.append(MatrixCell(service=name, change_type="removed"))

    for name, diff in report.changed.items():
        has_any = (
            bool(diff.added_keys)
            or bool(diff.removed_keys)
            or bool(diff.changed_keys)
        )
        change_type = "changed" if has_any else "unchanged"
        cells.append(MatrixCell(service=name, change_type=change_type))

    cells.sort(key=lambda c: c.service)
    return ChangeMatrix(cells=cells)
