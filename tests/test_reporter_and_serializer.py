"""Tests for stackdiff.reporter and stackdiff.serializer."""

from __future__ import annotations

import json

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport, build_report
from stackdiff.serializer import serialize


def _make_diffs(
    added=(), removed=(), changed_name=None, unchanged=()
) -> dict[str, ServiceDiff]:
    diffs: dict[str, ServiceDiff] = {}
    for name in added:
        diffs[name] = ServiceDiff(service=name, added=True)
    for name in removed:
        diffs[name] = ServiceDiff(service=name, removed=True)
    if changed_name:
        diffs[changed_name] = ServiceDiff(
            service=changed_name,
            changes={"image": ("nginx:1.24", "nginx:1.25")},
        )
    for name in unchanged:
        diffs[name] = ServiceDiff(service=name)
    return diffs


# ---------------------------------------------------------------------------
# build_report
# ---------------------------------------------------------------------------

def test_build_report_empty():
    report = build_report({})
    assert report.added == []
    assert report.removed == []
    assert report.changed == []
    assert report.unchanged == []
    assert report.summary["total"] == 0
    assert not report.has_changes()


def test_build_report_added():
    report = build_report(_make_diffs(added=["web"]))
    assert report.added == ["web"]
    assert report.has_changes()
    assert report.summary["added"] == 1


def test_build_report_removed():
    report = build_report(_make_diffs(removed=["db"]))
    assert report.removed == ["db"]
    assert report.has_changes()


def test_build_report_changed():
    report = build_report(_make_diffs(changed_name="proxy"))
    assert len(report.changed) == 1
    assert report.changed[0]["service"] == "proxy"
    assert "image" in report.changed[0]["changes"]
    assert report.has_changes()


def test_build_report_unchanged():
    report = build_report(_make_diffs(unchanged=["cache", "worker"]))
    assert report.unchanged == ["cache", "worker"]
    assert not report.has_changes()
    assert report.summary["unchanged"] == 2


def test_build_report_summary_counts():
    diffs = _make_diffs(
        added=["svc-a"],
        removed=["svc-b"],
        changed_name="svc-c",
        unchanged=["svc-d"],
    )
    report = build_report(diffs)
    assert report.summary == {
        "added": 1,
        "removed": 1,
        "changed": 1,
        "unchanged": 1,
        "total": 4,
    }


# ---------------------------------------------------------------------------
# serialize
# ---------------------------------------------------------------------------

def test_serialize_json_roundtrip():
    report = build_report(_make_diffs(added=["web"], unchanged=["db"]))
    output = serialize(report, fmt="json")
    data = json.loads(output)
    assert data["added"] == ["web"]
    assert data["summary"]["total"] == 2


def test_serialize_unsupported_format():
    report = DiffReport([], [], [], [], {"added": 0, "removed": 0, "changed": 0, "unchanged": 0, "total": 0})
    with pytest.raises(ValueError, match="Unsupported output format"):
        serialize(report, fmt="xml")  # type: ignore[arg-type]
