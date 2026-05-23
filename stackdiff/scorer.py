"""Scores the overall risk/impact of a diff report based on change magnitude."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from stackdiff.reporter import DiffReport
from stackdiff.differ import ServiceDiff

# Weight assigned to each category of change
_WEIGHTS: Dict[str, int] = {
    "added": 2,
    "removed": 3,
    "changed": 1,
}

# Per-field severity bump when a changed service touches critical keys
_CRITICAL_KEYS = {"image", "ports", "networks", "volumes", "command", "entrypoint"}
_CRITICAL_BUMP = 2


@dataclass
class RiskScore:
    total: int
    breakdown: Dict[str, int] = field(default_factory=dict)
    level: str = "low"

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "level": self.level,
            "breakdown": self.breakdown,
        }


def _level(total: int) -> str:
    if total == 0:
        return "none"
    if total <= 5:
        return "low"
    if total <= 15:
        return "medium"
    return "high"


def _score_diff(diff: ServiceDiff) -> int:
    """Return a numeric score for a single service diff."""
    score = 0
    if diff.status == "added":
        score += _WEIGHTS["added"]
    elif diff.status == "removed":
        score += _WEIGHTS["removed"]
    elif diff.status == "changed":
        score += _WEIGHTS["changed"]
        critical_hits = len(_CRITICAL_KEYS & set(diff.changes.keys()))
        score += critical_hits * _CRITICAL_BUMP
    return score


def score_report(report: DiffReport) -> RiskScore:
    """Compute an aggregate risk score for the entire diff report."""
    breakdown: Dict[str, int] = {}
    total = 0
    for name, diff in report.diffs.items():
        s = _score_diff(diff)
        if s:
            breakdown[name] = s
            total += s
    return RiskScore(total=total, breakdown=breakdown, level=_level(total))
