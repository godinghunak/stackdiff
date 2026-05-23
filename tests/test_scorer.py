"""Tests for stackdiff.scorer."""

from __future__ import annotations

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.scorer import RiskScore, _level, _score_diff, score_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_diff(
    name: str,
    status: str,
    changes: dict | None = None,
) -> ServiceDiff:
    return ServiceDiff(name=name, status=status, changes=changes or {})


def _make_report(*diffs: ServiceDiff) -> DiffReport:
    return DiffReport(diffs={d.name: d for d in diffs})


# ---------------------------------------------------------------------------
# _level
# ---------------------------------------------------------------------------

def test_level_none():
    assert _level(0) == "none"


def test_level_low():
    assert _level(3) == "low"
    assert _level(5) == "low"


def test_level_medium():
    assert _level(6) == "medium"
    assert _level(15) == "medium"


def test_level_high():
    assert _level(16) == "high"


# ---------------------------------------------------------------------------
# _score_diff
# ---------------------------------------------------------------------------

def test_score_added():
    assert _score_diff(_make_diff("svc", "added")) == 2


def test_score_removed():
    assert _score_diff(_make_diff("svc", "removed")) == 3


def test_score_changed_no_critical():
    diff = _make_diff("svc", "changed", {"environment": ("A", "B")})
    assert _score_diff(diff) == 1


def test_score_changed_with_critical_keys():
    diff = _make_diff("svc", "changed", {"image": ("v1", "v2"), "ports": ([], ["80:80"])})
    # base 1 + 2 critical keys * 2 bump = 5
    assert _score_diff(diff) == 5


# ---------------------------------------------------------------------------
# score_report
# ---------------------------------------------------------------------------

def test_score_empty_report():
    result = score_report(_make_report())
    assert result.total == 0
    assert result.level == "none"
    assert result.breakdown == {}


def test_score_report_added_and_removed():
    report = _make_report(
        _make_diff("alpha", "added"),
        _make_diff("beta", "removed"),
    )
    result = score_report(report)
    assert result.breakdown["alpha"] == 2
    assert result.breakdown["beta"] == 3
    assert result.total == 5
    assert result.level == "low"


def test_score_report_high_risk():
    diffs = [_make_diff(f"svc{i}", "removed") for i in range(6)]
    result = score_report(_make_report(*diffs))
    assert result.total == 18
    assert result.level == "high"


def test_to_dict_shape():
    report = _make_report(_make_diff("web", "added"))
    d = score_report(report).to_dict()
    assert set(d.keys()) == {"total", "level", "breakdown"}
    assert d["breakdown"]["web"] == 2
