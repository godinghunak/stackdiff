"""Tests for stackdiff.tagger."""

from __future__ import annotations

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.tagger import (
    TAG_ADDED,
    TAG_CONFIG_CHANGE,
    TAG_ENV_CHANGE,
    TAG_IMAGE_CHANGE,
    TAG_PORT_CHANGE,
    TAG_REMOVED,
    TAG_VOLUME_CHANGE,
    TagReport,
    tag_report,
)


def _make_diff(
    name: str = "web",
    added: bool = False,
    removed: bool = False,
    changes: list | None = None,
) -> ServiceDiff:
    return ServiceDiff(
        service=name,
        added=added,
        removed=removed,
        changes=changes or [],
    )


def _make_report(*diffs: ServiceDiff) -> DiffReport:
    return DiffReport(diffs=list(diffs))


def test_tag_report_empty():
    report = _make_report()
    tr = tag_report(report)
    assert tr.services == []
    assert tr.all_tags() == set()


def test_tag_added_service():
    report = _make_report(_make_diff("alpha", added=True))
    tr = tag_report(report)
    assert len(tr.services) == 1
    assert TAG_ADDED in tr.services[0].tags
    assert TAG_REMOVED not in tr.services[0].tags


def test_tag_removed_service():
    report = _make_report(_make_diff("beta", removed=True))
    tr = tag_report(report)
    assert TAG_REMOVED in tr.services[0].tags


def test_tag_image_change():
    diff = _make_diff(changes=[("image", ("nginx:1.24", "nginx:1.25"))])
    tr = tag_report(_make_report(diff))
    assert TAG_IMAGE_CHANGE in tr.services[0].tags


def test_tag_port_change():
    diff = _make_diff(changes=[("ports", (["80:80"], ["80:80", "443:443"]))])
    tr = tag_report(_make_report(diff))
    assert TAG_PORT_CHANGE in tr.services[0].tags


def test_tag_env_change():
    diff = _make_diff(changes=[("environment", ({}, {"DEBUG": "1"}))])
    tr = tag_report(_make_report(diff))
    assert TAG_ENV_CHANGE in tr.services[0].tags


def test_tag_volume_change():
    diff = _make_diff(changes=[("volumes", ([], ["/data:/data"]))])
    tr = tag_report(_make_report(diff))
    assert TAG_VOLUME_CHANGE in tr.services[0].tags


def test_services_with_tag_filters_correctly():
    r = _make_report(
        _make_diff("svc1", added=True),
        _make_diff("svc2", removed=True),
    )
    tr = tag_report(r)
    assert tr.services_with_tag(TAG_ADDED) == ["svc1"]
    assert tr.services_with_tag(TAG_REMOVED) == ["svc2"]


def test_to_dict_structure():
    diff = _make_diff(changes=[("image", ("a", "b"))])
    tr = tag_report(_make_report(diff))
    d = tr.to_dict()
    assert "services" in d
    entry = d["services"][0]
    assert "name" in entry
    assert "tags" in entry
    assert isinstance(entry["tags"], list)


def test_all_tags_union():
    r = _make_report(
        _make_diff("a", added=True),
        _make_diff("b", changes=[("image", ("x", "y"))]),
    )
    tr = tag_report(r)
    all_t = tr.all_tags()
    assert TAG_ADDED in all_t
    assert TAG_IMAGE_CHANGE in all_t
