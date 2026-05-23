"""Tests for stackdiff.profiler."""
import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.profiler import (
    ServiceProfile,
    ProfileReport,
    profile_report,
)


def _make_report(
    added=None,
    removed=None,
    changed=None,
) -> DiffReport:
    return DiffReport(
        added=added or [],
        removed=removed or [],
        changed=changed or {},
    )


def _make_diff(changed=None) -> ServiceDiff:
    return ServiceDiff(
        added=None,
        removed=None,
        changed=changed or {},
    )


# --- ServiceProfile ---

def test_complexity_score_sums_all_fields():
    p = ServiceProfile("svc", added_fields=2, removed_fields=1, changed_fields=3)
    assert p.complexity_score == 6


def test_complexity_score_zero_by_default():
    p = ServiceProfile("svc")
    assert p.complexity_score == 0


def test_to_dict_contains_expected_keys():
    p = ServiceProfile("web", added_fields=1, removed_fields=0, changed_fields=2)
    d = p.to_dict()
    assert d["service"] == "web"
    assert d["complexity_score"] == 3
    assert "added_fields" in d
    assert "removed_fields" in d
    assert "changed_fields" in d


# --- ProfileReport ---

def test_most_complex_returns_none_for_empty():
    pr = ProfileReport()
    assert pr.most_complex is None


def test_most_complex_returns_highest_score():
    pr = ProfileReport(profiles=[
        ServiceProfile("a", changed_fields=1),
        ServiceProfile("b", changed_fields=5),
        ServiceProfile("c", added_fields=2),
    ])
    assert pr.most_complex.service_name == "b"


def test_profile_report_to_dict_structure():
    pr = ProfileReport(profiles=[ServiceProfile("x", added_fields=1)])
    d = pr.to_dict()
    assert "profiles" in d
    assert "most_complex" in d
    assert d["most_complex"] == "x"


# --- profile_report ---

def test_profile_report_empty():
    report = _make_report()
    result = profile_report(report)
    assert result.profiles == []
    assert result.most_complex is None


def test_profile_report_added_services():
    report = _make_report(added=["alpha", "beta"])
    result = profile_report(report)
    names = {p.service_name for p in result.profiles}
    assert names == {"alpha", "beta"}
    for p in result.profiles:
        assert p.added_fields == 1


def test_profile_report_removed_services():
    report = _make_report(removed=["old-svc"])
    result = profile_report(report)
    assert len(result.profiles) == 1
    assert result.profiles[0].removed_fields == 1


def test_profile_report_changed_services():
    diff = _make_diff(changed={"image": ("v1", "v2"), "ports": ("80", "8080")})
    report = _make_report(changed={"web": diff})
    result = profile_report(report)
    assert len(result.profiles) == 1
    p = result.profiles[0]
    assert p.service_name == "web"
    assert p.changed_fields == 2


def test_profile_report_sorted_by_complexity_descending():
    diff_big = _make_diff(changed={"a": (1, 2), "b": (3, 4), "c": (5, 6)})
    diff_small = _make_diff(changed={"x": (1, 2)})
    report = _make_report(
        added=["new-svc"],
        changed={"heavy": diff_big, "light": diff_small},
    )
    result = profile_report(report)
    scores = [p.complexity_score for p in result.profiles]
    assert scores == sorted(scores, reverse=True)
    assert result.profiles[0].service_name == "heavy"
