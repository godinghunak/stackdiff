"""Tests for stackdiff.differ_matrix and stackdiff.cli_matrix."""
from __future__ import annotations

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.differ_matrix import MatrixCell, ChangeMatrix, build_matrix
from stackdiff.cli_matrix import render_matrix


def _make_diff(
    added=None, removed=None, changed=None
) -> ServiceDiff:
    return ServiceDiff(
        added_keys=added or {},
        removed_keys=removed or {},
        changed_keys=changed or {},
    )


def _make_report(
    added=None, removed=None, changed=None
) -> DiffReport:
    return DiffReport(
        added=added or [],
        removed=removed or [],
        changed=changed or {},
    )


# --- MatrixCell ---

def test_matrix_cell_to_dict():
    cell = MatrixCell(service="web", change_type="added")
    d = cell.to_dict()
    assert d == {"service": "web", "change_type": "added"}


# --- ChangeMatrix ---

def test_change_matrix_services_by_type_empty():
    m = ChangeMatrix()
    assert m.services_by_type("added") == []


def test_change_matrix_services_by_type_filters_correctly():
    cells = [
        MatrixCell("alpha", "added"),
        MatrixCell("beta", "removed"),
        MatrixCell("gamma", "added"),
    ]
    m = ChangeMatrix(cells=cells)
    assert set(m.services_by_type("added")) == {"alpha", "gamma"}
    assert m.services_by_type("removed") == ["beta"]


def test_change_matrix_to_dict_summary_counts():
    cells = [
        MatrixCell("a", "added"),
        MatrixCell("b", "removed"),
        MatrixCell("c", "changed"),
        MatrixCell("d", "unchanged"),
    ]
    m = ChangeMatrix(cells=cells)
    summary = m.to_dict()["summary"]
    assert summary == {"added": 1, "removed": 1, "changed": 1, "unchanged": 1}


# --- build_matrix ---

def test_build_matrix_empty_report():
    report = _make_report()
    matrix = build_matrix(report)
    assert matrix.cells == []


def test_build_matrix_added_services():
    report = _make_report(added=["web", "db"])
    matrix = build_matrix(report)
    types = {c.service: c.change_type for c in matrix.cells}
    assert types["web"] == "added"
    assert types["db"] == "added"


def test_build_matrix_removed_services():
    report = _make_report(removed=["cache"])
    matrix = build_matrix(report)
    assert matrix.cells[0].change_type == "removed"


def test_build_matrix_changed_service_with_diff():
    diff = _make_diff(changed={"image": ("v1", "v2")})
    report = _make_report(changed={"web": diff})
    matrix = build_matrix(report)
    assert matrix.cells[0].change_type == "changed"


def test_build_matrix_unchanged_service_no_diff():
    diff = _make_diff()
    report = _make_report(changed={"web": diff})
    matrix = build_matrix(report)
    assert matrix.cells[0].change_type == "unchanged"


def test_build_matrix_cells_sorted_by_name():
    report = _make_report(added=["zebra", "alpha", "mango"])
    matrix = build_matrix(report)
    names = [c.service for c in matrix.cells]
    assert names == sorted(names)


# --- render_matrix ---

def test_render_matrix_empty():
    m = ChangeMatrix()
    lines = render_matrix(m)
    assert lines == ["No services found in either file."]


def test_render_matrix_contains_service_name():
    m = ChangeMatrix(cells=[MatrixCell("web", "added")])
    output = "\n".join(render_matrix(m))
    assert "web" in output
    assert "+" in output


def test_render_matrix_summary_line_present():
    m = ChangeMatrix(cells=[MatrixCell("db", "removed")])
    output = "\n".join(render_matrix(m))
    assert "removed=1" in output
