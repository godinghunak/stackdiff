"""Tests for stackdiff.differ_stats."""

from __future__ import annotations

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.differ_stats import DiffStats, compute_stats


def _make_diff(name: str) -> ServiceDiff:
    return ServiceDiff(service=name, added={}, removed={}, changed={})


def _make_report(
    added: list[str] | None = None,
    removed: list[str] | None = None,
    changed: list[str] | None = None,
    unchanged: list[str] | None = None,
) -> DiffReport:
    return DiffReport(
        added=[_make_diff(n) for n in (added or [])],
        removed=[_make_diff(n) for n in (removed or [])],
        changed=[_make_diff(n) for n in (changed or [])],
        unchanged=list(unchanged or []),
    )


def test_compute_stats_empty_report():
    report = _make_report()
    stats = compute_stats(report)
    assert stats.total_services == 0
    assert stats.added == 0
    assert stats.removed == 0
    assert stats.changed == 0
    assert stats.unchanged == 0


def test_compute_stats_change_rate_zero_when_no_services():
    stats = compute_stats(_make_report())
    assert stats.change_rate == 0.0


def test_compute_stats_counts_added():
    report = _make_report(added=["web", "db"])
    stats = compute_stats(report)
    assert stats.added == 2
    assert stats.total_services == 2


def test_compute_stats_counts_removed():
    report = _make_report(removed=["cache"])
    stats = compute_stats(report)
    assert stats.removed == 1
    assert stats.total_services == 1


def test_compute_stats_counts_changed():
    report = _make_report(changed=["api"])
    stats = compute_stats(report)
    assert stats.changed == 1


def test_compute_stats_counts_unchanged():
    report = _make_report(unchanged=["worker", "scheduler"])
    stats = compute_stats(report)
    assert stats.unchanged == 2
    assert stats.total_services == 2


def test_compute_stats_mixed():
    report = _make_report(
        added=["new"],
        removed=["old"],
        changed=["api"],
        unchanged=["worker", "db"],
    )
    stats = compute_stats(report)
    assert stats.total_services == 5
    assert stats.added == 1
    assert stats.removed == 1
    assert stats.changed == 1
    assert stats.unchanged == 2


def test_change_rate_all_changed():
    report = _make_report(changed=["a", "b", "c"])
    stats = compute_stats(report)
    assert stats.change_rate == pytest.approx(1.0)


def test_change_rate_partial():
    report = _make_report(changed=["a"], unchanged=["b", "c", "d"])
    stats = compute_stats(report)
    assert stats.change_rate == pytest.approx(0.25)


def test_to_dict_keys():
    report = _make_report(added=["x"], unchanged=["y"])
    d = compute_stats(report).to_dict()
    assert set(d.keys()) == {
        "total_services",
        "added",
        "removed",
        "changed",
        "unchanged",
        "change_rate",
    }
    assert d["added"] == 1
    assert d["unchanged"] == 1
