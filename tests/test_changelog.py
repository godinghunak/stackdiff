"""Tests for stackdiff.changelog and stackdiff.cli_changelog."""

from __future__ import annotations

import argparse
from unittest.mock import patch, MagicMock

import pytest

from stackdiff.changelog import (
    ChangelogEntry,
    build_changelog_entry,
    render_changelog,
)
from stackdiff.reporter import DiffReport
from stackdiff.differ import ServiceDiff


FIXED_TS = "2024-01-01T00:00:00+00:00"


def _make_report(
    added=(),
    removed=(),
    changed: dict | None = None,
) -> DiffReport:
    diffs = {}
    if changed:
        for name, diff in changed.items():
            diffs[name] = diff
    return DiffReport(added=list(added), removed=list(removed), changed=diffs)


def _make_diff(**kwargs) -> ServiceDiff:
    defaults = dict(added={}, removed={}, modified={})
    defaults.update(kwargs)
    return ServiceDiff(**defaults)


# --- ChangelogEntry ---

def test_is_empty_when_no_changes():
    entry = ChangelogEntry(version="1.0", timestamp=FIXED_TS)
    assert entry.is_empty()


def test_is_not_empty_with_added():
    entry = ChangelogEntry(version="1.0", timestamp=FIXED_TS, added=["web"])
    assert not entry.is_empty()


def test_to_dict_keys():
    entry = ChangelogEntry(version="1.0", timestamp=FIXED_TS, added=["web"])
    d = entry.to_dict()
    assert set(d.keys()) == {"version", "timestamp", "added", "removed", "changed"}


# --- build_changelog_entry ---

def test_build_changelog_entry_empty_report():
    report = _make_report()
    entry = build_changelog_entry(report, version="0.1", timestamp=FIXED_TS)
    assert entry.version == "0.1"
    assert entry.timestamp == FIXED_TS
    assert entry.is_empty()


def test_build_changelog_entry_populates_added():
    report = _make_report(added=["db", "cache"])
    entry = build_changelog_entry(report, version="1.0", timestamp=FIXED_TS)
    assert sorted(entry.added) == ["cache", "db"]


def test_build_changelog_entry_populates_removed():
    report = _make_report(removed=["legacy"])
    entry = build_changelog_entry(report, version="1.0", timestamp=FIXED_TS)
    assert entry.removed == ["legacy"]


def test_build_changelog_entry_populates_changed():
    report = _make_report(changed={"web": _make_diff(modified={"image": ("a", "b")})})
    entry = build_changelog_entry(report, version="1.0", timestamp=FIXED_TS)
    assert entry.changed == ["web"]


def test_build_changelog_entry_uses_current_time_when_no_timestamp():
    report = _make_report()
    entry = build_changelog_entry(report, version="1.0")
    assert entry.timestamp  # non-empty
    assert entry.timestamp != FIXED_TS


# --- render_changelog ---

def test_render_changelog_no_changes():
    entry = ChangelogEntry(version="0.0.1", timestamp=FIXED_TS)
    output = render_changelog(entry)
    assert "No changes" in output
    assert "0.0.1" in output


def test_render_changelog_includes_added_section():
    entry = ChangelogEntry(version="1.0", timestamp=FIXED_TS, added=["web"])
    output = render_changelog(entry)
    assert "### Added" in output
    assert "`web`" in output


def test_render_changelog_includes_removed_section():
    entry = ChangelogEntry(version="1.0", timestamp=FIXED_TS, removed=["old"])
    output = render_changelog(entry)
    assert "### Removed" in output
    assert "`old`" in output


def test_render_changelog_includes_changed_section():
    entry = ChangelogEntry(version="1.0", timestamp=FIXED_TS, changed=["api"])
    output = render_changelog(entry)
    assert "### Changed" in output
    assert "`api`" in output
