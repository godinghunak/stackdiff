"""Tests for stackdiff.formatter."""

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.formatter import format_diff, SEPARATOR


def make_diff(
    added=None,
    removed=None,
    changed=None,
    unchanged=None,
):
    return ServiceDiff(
        added=set(added or []),
        removed=set(removed or []),
        changed=changed or {},
        unchanged=set(unchanged or []),
    )


def test_format_no_diff():
    diff = make_diff(unchanged=["web", "db"])
    output = format_diff(diff)
    assert "No differences found." in output
    assert SEPARATOR in output


def test_format_added_services():
    diff = make_diff(added=["cache", "worker"])
    output = format_diff(diff)
    assert "Added services:" in output
    assert "+ cache" in output
    assert "+ worker" in output


def test_format_removed_services():
    diff = make_diff(removed=["legacy"])
    output = format_diff(diff)
    assert "Removed services:" in output
    assert "- legacy" in output


def test_format_changed_services():
    diff = make_diff(
        changed={"web": {"image": ("nginx:1.21", "nginx:1.25")}}
    )
    output = format_diff(diff)
    assert "Changed services:" in output
    assert "~ web" in output
    assert "'nginx:1.21'" in output
    assert "'nginx:1.25'" in output


def test_format_combined():
    diff = make_diff(
        added=["cache"],
        removed=["legacy"],
        changed={"web": {"image": ("v1", "v2")}},
    )
    output = format_diff(diff)
    assert "Added" in output
    assert "Removed" in output
    assert "Changed" in output


def test_format_color_applies_ansi():
    diff = make_diff(added=["cache"], removed=["old"])
    output = format_diff(diff, color=True)
    assert "\033[32m" in output  # green for added
    assert "\033[31m" in output  # red for removed
    assert "\033[0m" in output   # reset


def test_format_no_color_no_ansi():
    diff = make_diff(added=["cache"])
    output = format_diff(diff, color=False)
    assert "\033[" not in output
