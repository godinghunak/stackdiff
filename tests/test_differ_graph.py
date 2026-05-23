"""Tests for stackdiff.differ_graph."""
from __future__ import annotations

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.differ_graph import GraphNode, DiffGraph, build_graph
from stackdiff.reporter import DiffReport


def _make_report(
    added=(), removed=(), changed=()
) -> DiffReport:
    return DiffReport(
        added=list(added),
        removed=list(removed),
        changed={name: ServiceDiff(name=name, added={}, removed={}, changed={}) for name in changed},
    )


def _raw(*names, deps: dict | None = None) -> dict:
    """Build a minimal raw_services mapping."""
    deps = deps or {}
    return {n: {"depends_on": deps.get(n, [])} for n in names}


# ---------------------------------------------------------------------------
# GraphNode
# ---------------------------------------------------------------------------

def test_graph_node_to_dict():
    node = GraphNode(name="web", change_type="added", depends_on=["db"])
    d = node.to_dict()
    assert d["name"] == "web"
    assert d["change_type"] == "added"
    assert d["depends_on"] == ["db"]


# ---------------------------------------------------------------------------
# DiffGraph helpers
# ---------------------------------------------------------------------------

def test_all_service_names_sorted():
    report = _make_report(added=["web", "db"])
    raw = _raw("web", "db")
    graph = build_graph(report, raw)
    assert graph.all_service_names() == ["db", "web"]


def test_neighbours_returns_deps():
    report = _make_report(added=["web", "db"])
    raw = {"web": {"depends_on": ["db"]}, "db": {}}
    graph = build_graph(report, raw)
    assert graph.neighbours("web") == ["db"]
    assert graph.neighbours("db") == []


def test_neighbours_missing_node_returns_empty():
    graph = DiffGraph()
    assert graph.neighbours("ghost") == []


def test_affected_by():
    report = _make_report(added=["web", "db"])
    raw = {"web": {"depends_on": ["db"]}, "db": {}}
    graph = build_graph(report, raw)
    assert graph.affected_by("db") == ["web"]
    assert graph.affected_by("web") == []


# ---------------------------------------------------------------------------
# build_graph — change type assignment
# ---------------------------------------------------------------------------

def test_build_graph_added_service():
    report = _make_report(added=["web"])
    graph = build_graph(report, _raw("web"))
    assert graph.nodes["web"].change_type == "added"


def test_build_graph_removed_service():
    report = _make_report(removed=["cache"])
    graph = build_graph(report, _raw("cache"))
    assert graph.nodes["cache"].change_type == "removed"


def test_build_graph_changed_service():
    report = _make_report(changed=["api"])
    graph = build_graph(report, _raw("api"))
    assert graph.nodes["api"].change_type == "changed"


def test_build_graph_unchanged_service():
    report = _make_report()
    graph = build_graph(report, _raw("db"))
    assert graph.nodes["db"].change_type == "unchanged"


def test_build_graph_dict_depends_on():
    """depends_on can be a dict (long-form) in compose v3."""
    report = _make_report(added=["web"])
    raw = {"web": {"depends_on": {"db": {"condition": "service_healthy"}}}, "db": {}}
    graph = build_graph(report, raw)
    assert graph.nodes["web"].depends_on == ["db"]


def test_to_dict_structure():
    report = _make_report(added=["web"])
    graph = build_graph(report, _raw("web"))
    d = graph.to_dict()
    assert "web" in d
    assert set(d["web"].keys()) == {"name", "change_type", "depends_on"}
