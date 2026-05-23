"""Tests for stackdiff.snapshotter and stackdiff.snapshot_compare."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.snapshotter import save_snapshot, load_snapshot, SnapshotError, Snapshot
from stackdiff.snapshot_compare import compare_against_snapshot, _compare


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_report(
    added: set[str] | None = None,
    removed: set[str] | None = None,
    changed: dict[str, ServiceDiff] | None = None,
) -> DiffReport:
    return DiffReport(
        added=added or set(),
        removed=removed or set(),
        changed=changed or {},
    )


def _make_diff(name: str, added=(), removed=(), changed=()) -> ServiceDiff:
    return ServiceDiff(
        name=name,
        added_keys=set(added),
        removed_keys=set(removed),
        changed_keys=set(changed),
    )


# ---------------------------------------------------------------------------
# save_snapshot / load_snapshot
# ---------------------------------------------------------------------------

def test_save_snapshot_creates_file(tmp_path: Path) -> None:
    report = _make_report(added={"web"}, removed={"db"})
    dest = tmp_path / "snap.json"
    snap = save_snapshot(report, dest)
    assert dest.exists()
    assert isinstance(snap, Snapshot)


def test_save_snapshot_content_is_valid_json(tmp_path: Path) -> None:
    report = _make_report(added={"api"})
    dest = tmp_path / "snap.json"
    save_snapshot(report, dest)
    data = json.loads(dest.read_text())
    assert "added" in data
    assert "api" in data["added"]


def test_load_snapshot_round_trips(tmp_path: Path) -> None:
    diff = _make_diff("svc", added=["ports"], changed=["image"])
    report = _make_report(added={"new"}, removed={"old"}, changed={"svc": diff})
    dest = tmp_path / "snap.json"
    save_snapshot(report, dest)
    loaded = load_snapshot(dest)
    assert loaded.added == {"new"}
    assert loaded.removed == {"old"}
    assert "svc" in loaded.changed
    assert loaded.changed["svc"].added_keys == {"ports"}


def test_load_snapshot_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(tmp_path / "nonexistent.json")


def test_load_snapshot_invalid_json_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(SnapshotError):
        load_snapshot(bad)


# ---------------------------------------------------------------------------
# compare_against_snapshot
# ---------------------------------------------------------------------------

def test_compare_new_addition_detected() -> None:
    baseline = _make_report(added={"old_add"})
    current = _make_report(added={"old_add", "new_add"})
    cmp = _compare(current, baseline)
    assert "new_add" in cmp.new_additions


def test_compare_resolved_removal_detected() -> None:
    baseline = _make_report(removed={"gone"})
    current = _make_report()
    cmp = _compare(current, baseline)
    assert "gone" in cmp.resolved_removals


def test_compare_against_snapshot_missing_returns_warning(tmp_path: Path) -> None:
    report = _make_report(added={"svc"})
    _, warning = compare_against_snapshot(report, tmp_path / "missing.json")
    assert warning is not None
    assert "missing" in warning.lower() or "not found" in warning.lower()


def test_has_regressions_false_when_clean() -> None:
    baseline = _make_report(added={"a"})
    current = _make_report(added={"a"})
    cmp = _compare(current, baseline)
    assert not cmp.has_regressions


def test_to_dict_contains_all_keys() -> None:
    cmp = _compare(_make_report(added={"x"}), _make_report())
    d = cmp.to_dict()
    for key in ("new_additions", "new_removals", "resolved_additions",
                "resolved_removals", "new_changed", "resolved_changed",
                "has_regressions"):
        assert key in d
