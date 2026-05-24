"""Tests for stackdiff.differ_heatmap."""
from __future__ import annotations

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.differ_heatmap import (
    HeatmapEntry,
    DiffHeatmap,
    build_heatmap,
    _count_changes,
)


def _make_diff(
    added: list | None = None,
    removed: list | None = None,
    changed: list | None = None,
) -> ServiceDiff:
    return ServiceDiff(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def _make_report(changes: dict) -> DiffReport:
    return DiffReport(
        added_services=[],
        removed_services=[],
        changes=changes,
    )


# --- HeatmapEntry ---

def test_entry_to_dict_keys():
    e = HeatmapEntry(service="web", change_count=3, change_types=["added", "changed"])
    d = e.to_dict()
    assert set(d.keys()) == {"service", "change_count", "change_types"}


def test_entry_change_types_sorted():
    e = HeatmapEntry(service="db", change_count=2, change_types=["changed", "added"])
    assert e.to_dict()["change_types"] == ["added", "changed"]


# --- _count_changes ---

def test_count_changes_empty():
    count, types = _count_changes(_make_diff())
    assert count == 0
    assert types == []


def test_count_changes_only_added():
    count, types = _count_changes(_make_diff(added=["ports"]))
    assert count == 1
    assert "added" in types


def test_count_changes_all_types():
    count, types = _count_changes(_make_diff(added=["a"], removed=["b", "c"], changed=["d"]))
    assert count == 4
    assert set(types) == {"added", "removed", "changed"}


# --- build_heatmap ---

def test_build_heatmap_empty_report():
    heatmap = build_heatmap(_make_report({}))
    assert heatmap.entries == []


def test_build_heatmap_skips_unchanged_services():
    report = _make_report({"web": _make_diff()})
    heatmap = build_heatmap(report)
    assert heatmap.entries == []


def test_build_heatmap_single_service():
    report = _make_report({"api": _make_diff(added=["env"], changed=["image"])})
    heatmap = build_heatmap(report)
    assert len(heatmap.entries) == 1
    assert heatmap.entries[0].service == "api"
    assert heatmap.entries[0].change_count == 2


def test_build_heatmap_sorted_descending():
    report = _make_report({
        "low": _make_diff(added=["x"]),
        "high": _make_diff(added=["a", "b", "c"]),
        "mid": _make_diff(changed=["y", "z"]),
    })
    heatmap = build_heatmap(report)
    counts = [e.change_count for e in heatmap.entries]
    assert counts == sorted(counts, reverse=True)


def test_build_heatmap_hottest():
    report = _make_report({
        "svc_a": _make_diff(added=["a"]),
        "svc_b": _make_diff(added=["a", "b", "c"]),
    })
    heatmap = build_heatmap(report)
    assert heatmap.hottest().service == "svc_b"  # type: ignore[union-attr]


def test_build_heatmap_hottest_none_when_empty():
    assert DiffHeatmap().hottest() is None


def test_build_heatmap_to_dict_structure():
    report = _make_report({"web": _make_diff(removed=["ports"])})
    d = build_heatmap(report).to_dict()
    assert "entries" in d
    assert d["entries"][0]["service"] == "web"
