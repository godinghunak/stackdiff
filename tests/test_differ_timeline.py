"""Tests for stackdiff.differ_timeline."""

from __future__ import annotations

from stackdiff.differ import ServiceDiff
from stackdiff.differ_timeline import (
    DiffTimeline,
    TimelineEvent,
    build_timeline_event,
    record_event,
)
from stackdiff.reporter import DiffReport


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_diff(before: dict, after: dict) -> ServiceDiff:
    return ServiceDiff(before=before, after=after)


def _make_report(
    added=(),
    removed=(),
    changed: dict | None = None,
) -> DiffReport:
    return DiffReport(
        added=list(added),
        removed=list(removed),
        changed=changed or {},
    )


# ---------------------------------------------------------------------------
# TimelineEvent
# ---------------------------------------------------------------------------

def test_event_is_empty_when_no_services():
    ev = TimelineEvent(timestamp="t", added=[], removed=[], changed=[])
    assert ev.is_empty()


def test_event_not_empty_with_added():
    ev = TimelineEvent(timestamp="t", added=["web"], removed=[], changed=[])
    assert not ev.is_empty()


def test_event_to_dict_keys():
    ev = TimelineEvent(timestamp="2024-01-01", added=["a"], removed=[], changed=["b"])
    d = ev.to_dict()
    assert set(d.keys()) == {"timestamp", "added", "removed", "changed"}
    assert d["added"] == ["a"]
    assert d["changed"] == ["b"]


# ---------------------------------------------------------------------------
# build_timeline_event
# ---------------------------------------------------------------------------

def test_build_timeline_event_captures_added():
    report = _make_report(added=["web", "db"])
    ev = build_timeline_event(report, timestamp="2024-06-01T00:00:00+00:00")
    assert sorted(ev.added) == ["db", "web"]
    assert ev.removed == []
    assert ev.changed == []


def test_build_timeline_event_captures_changed():
    diff = _make_diff({"image": "old"}, {"image": "new"})
    report = _make_report(changed={"api": diff})
    ev = build_timeline_event(report, timestamp="T")
    assert ev.changed == ["api"]


def test_build_timeline_event_uses_provided_timestamp():
    report = _make_report()
    ev = build_timeline_event(report, timestamp="fixed-ts")
    assert ev.timestamp == "fixed-ts"


def test_build_timeline_event_generates_timestamp_when_none():
    report = _make_report()
    ev = build_timeline_event(report)
    assert ev.timestamp  # non-empty string


# ---------------------------------------------------------------------------
# DiffTimeline / record_event
# ---------------------------------------------------------------------------

def test_timeline_starts_empty():
    tl = DiffTimeline()
    assert tl.events == []


def test_record_event_appends_to_timeline():
    tl = DiffTimeline()
    report = _make_report(added=["web"])
    record_event(tl, report, timestamp="T1")
    assert len(tl.events) == 1
    assert tl.events[0].added == ["web"]


def test_services_ever_changed_deduplicates():
    tl = DiffTimeline()
    record_event(tl, _make_report(added=["web"]), timestamp="T1")
    record_event(tl, _make_report(added=["web", "db"]), timestamp="T2")
    services = tl.services_ever_changed()
    assert sorted(services) == ["db", "web"]


def test_timeline_to_dict_structure():
    tl = DiffTimeline()
    record_event(tl, _make_report(removed=["cache"]), timestamp="T")
    d = tl.to_dict()
    assert "events" in d
    assert len(d["events"]) == 1
    assert d["events"][0]["removed"] == ["cache"]
