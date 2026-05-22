"""Tests for stackdiff.summarizer."""

from __future__ import annotations

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.summarizer import SummaryLine, render_summary, summarize_report


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


def _make_diff(fields: list[str]) -> ServiceDiff:
    return ServiceDiff(
        name="svc",
        changes={f: ("old", "new") for f in fields},
    )


# ---------------------------------------------------------------------------
# summarize_report
# ---------------------------------------------------------------------------


def test_no_changes_returns_unchanged_line():
    report = _make_report()
    lines = summarize_report(report)
    assert len(lines) == 1
    assert lines[0].category == "unchanged"
    assert "No service-level changes" in lines[0].text


def test_added_services_appear_in_summary():
    report = _make_report(added=["alpha", "beta"])
    lines = summarize_report(report)
    categories = [l.category for l in lines]
    assert "added" in categories
    added_line = next(l for l in lines if l.category == "added")
    assert "alpha" in added_line.text
    assert "beta" in added_line.text
    assert "Added (2)" in added_line.text


def test_removed_services_appear_in_summary():
    report = _make_report(removed=["gamma"])
    lines = summarize_report(report)
    removed_line = next(l for l in lines if l.category == "removed")
    assert "gamma" in removed_line.text
    assert "Removed (1)" in removed_line.text


def test_changed_services_list_modified_fields():
    diff = ServiceDiff(name="web", changes={"image": ("v1", "v2"), "ports": ("80", "8080")})
    report = _make_report(changed={"web": diff})
    lines = summarize_report(report)
    changed_line = next(l for l in lines if l.category == "changed")
    assert "web" in changed_line.text
    assert "2 fields" in changed_line.text
    assert "image" in changed_line.text
    assert "ports" in changed_line.text


def test_total_count_headline():
    report = _make_report(added=["a"], removed=["b"])
    lines = summarize_report(report)
    headline = lines[0]
    assert "2 services affected" in headline.text


def test_singular_service_headline():
    report = _make_report(added=["only"])
    lines = summarize_report(report)
    assert "1 service affected" in lines[0].text


# ---------------------------------------------------------------------------
# render_summary
# ---------------------------------------------------------------------------


def test_render_summary_no_changes():
    report = _make_report()
    text = render_summary(report)
    assert "No service-level changes" in text


def test_render_summary_multiline():
    diff = ServiceDiff(name="db", changes={"image": ("postgres:14", "postgres:15")})
    report = _make_report(added=["cache"], changed={"db": diff})
    text = render_summary(report)
    lines = text.splitlines()
    assert len(lines) >= 3  # headline + added + changed
    assert any("cache" in l for l in lines)
    assert any("db" in l for l in lines)
