"""Tests for stackdiff.filter and stackdiff.sorter."""

import pytest

from stackdiff.reporter import DiffReport
from stackdiff.differ import ServiceDiff
from stackdiff.filter import FilterOptions, filter_report
from stackdiff.sorter import sort_report


def _make_report() -> DiffReport:
    return DiffReport(
        added=["web", "worker"],
        removed=["legacy"],
        changed={
            "db": ServiceDiff(
                service="db",
                added_keys=["healthcheck"],
                removed_keys=[],
                changed_keys={"image": ("postgres:14", "postgres:15")},
            )
        },
    )


def test_filter_exclude_added():
    report = filter_report(_make_report(), FilterOptions(include_added=False))
    assert report.added == []
    assert report.removed == ["legacy"]
    assert "db" in report.changed


def test_filter_exclude_removed():
    report = filter_report(_make_report(), FilterOptions(include_removed=False))
    assert report.removed == []
    assert report.added == ["web", "worker"]


def test_filter_exclude_changed():
    report = filter_report(_make_report(), FilterOptions(include_changed=False))
    assert report.changed == {}


def test_filter_by_service_names():
    report = filter_report(
        _make_report(), FilterOptions(service_names={"web", "db"})
    )
    assert report.added == ["web"]
    assert report.removed == []
    assert list(report.changed.keys()) == ["db"]


def test_filter_service_names_none_keeps_all():
    original = _make_report()
    report = filter_report(original, FilterOptions(service_names=None))
    assert report.added == original.added
    assert report.removed == original.removed
    assert set(report.changed.keys()) == set(original.changed.keys())


def test_sort_report_orders_alphabetically():
    unsorted = DiffReport(
        added=["worker", "api", "cache"],
        removed=["zz", "aa"],
        changed={
            "z_svc": ServiceDiff(service="z_svc", added_keys=[], removed_keys=[], changed_keys={}),
            "a_svc": ServiceDiff(service="a_svc", added_keys=[], removed_keys=[], changed_keys={}),
        },
    )
    result = sort_report(unsorted)
    assert result.added == ["api", "cache", "worker"]
    assert result.removed == ["aa", "zz"]
    assert list(result.changed.keys()) == ["a_svc", "z_svc"]


def test_sort_report_empty():
    empty = DiffReport(added=[], removed=[], changed={})
    result = sort_report(empty)
    assert result.added == []
    assert result.removed == []
    assert result.changed == {}
