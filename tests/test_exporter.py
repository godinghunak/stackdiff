"""Tests for stackdiff.exporter."""

from __future__ import annotations

import json
import pathlib

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.exporter import ExportError, detect_format, export_report
from stackdiff.reporter import DiffReport


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


# ---------------------------------------------------------------------------
# detect_format
# ---------------------------------------------------------------------------


def test_detect_format_json():
    assert detect_format(pathlib.Path("out.json")) == "json"


def test_detect_format_text_for_txt():
    assert detect_format(pathlib.Path("out.txt")) == "text"


def test_detect_format_text_fallback():
    assert detect_format(pathlib.Path("out.md")) == "text"


# ---------------------------------------------------------------------------
# export_report – json
# ---------------------------------------------------------------------------


def test_export_json_creates_valid_json(tmp_path):
    report = _make_report(added=["web"])
    dest = tmp_path / "report.json"
    export_report(report, dest, fmt="json")
    data = json.loads(dest.read_text())
    assert "added" in data
    assert "web" in data["added"]


def test_export_json_no_changes(tmp_path):
    report = _make_report()
    dest = tmp_path / "empty.json"
    export_report(report, dest, fmt="json")
    data = json.loads(dest.read_text())
    assert data["added"] == []
    assert data["removed"] == []
    assert data["changed"] == {}


# ---------------------------------------------------------------------------
# export_report – text
# ---------------------------------------------------------------------------


def test_export_text_creates_readable_file(tmp_path):
    diff = ServiceDiff(name="db", changes={"image": ("v1", "v2")})
    report = _make_report(changed={"db": diff})
    dest = tmp_path / "report.txt"
    export_report(report, dest, fmt="text")
    content = dest.read_text()
    assert "db" in content


def test_export_text_no_changes_message(tmp_path):
    report = _make_report()
    dest = tmp_path / "report.txt"
    export_report(report, dest, fmt="text")
    assert "No service-level changes" in dest.read_text()


# ---------------------------------------------------------------------------
# export_report – error cases
# ---------------------------------------------------------------------------


def test_export_unsupported_format_raises(tmp_path):
    report = _make_report()
    with pytest.raises(ExportError, match="Unsupported export format"):
        export_report(report, tmp_path / "out.xml", fmt="xml")  # type: ignore[arg-type]


def test_export_bad_path_raises(tmp_path):
    report = _make_report()
    missing_parent = tmp_path / "nonexistent" / "report.json"
    with pytest.raises(ExportError, match="Failed to write"):
        export_report(report, missing_parent, fmt="json")
