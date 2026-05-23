"""Tests for stackdiff.cli_graph."""
from __future__ import annotations

import argparse
import os
import textwrap
from pathlib import Path

import pytest

from stackdiff.cli_graph import render_graph, build_graph_parser, run_graph
from stackdiff.differ_graph import DiffGraph, GraphNode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content))
    return path


@pytest.fixture()
def compose_dir(tmp_path):
    return tmp_path


class _NS:
    """Minimal argparse.Namespace stand-in."""
    def __init__(self, a, b, no_color=False):
        self.file_a = a
        self.file_b = b
        self.no_color = no_color


# ---------------------------------------------------------------------------
# render_graph
# ---------------------------------------------------------------------------

def _simple_graph() -> DiffGraph:
    g = DiffGraph()
    g.nodes["db"] = GraphNode("db", "unchanged", [])
    g.nodes["web"] = GraphNode("web", "added", ["db"])
    return g


def test_render_graph_empty():
    assert render_graph(DiffGraph()) == "(no services)"


def test_render_graph_shows_symbol():
    out = render_graph(_simple_graph())
    assert "[+] web" in out
    assert "[ ] db" in out


def test_render_graph_shows_dependency_arrow():
    out = render_graph(_simple_graph())
    assert "-> db" in out


def test_render_graph_shows_needed_by():
    out = render_graph(_simple_graph())
    assert "needed by: web" in out


# ---------------------------------------------------------------------------
# run_graph integration
# ---------------------------------------------------------------------------

def test_run_graph_no_changes(compose_dir, capsys):
    content = """\
        version: '3'
        services:
          db:
            image: postgres:15
    """
    a = _write(compose_dir / "a.yml", content)
    b = _write(compose_dir / "b.yml", content)
    code = run_graph(_NS(str(a), str(b)))
    out = capsys.readouterr().out
    assert code == 0
    assert "db" in out


def test_run_graph_added_service(compose_dir, capsys):
    a = _write(compose_dir / "a.yml", "version: '3'\nservices:\n  db:\n    image: postgres\n")
    b = _write(
        compose_dir / "b.yml",
        "version: '3'\nservices:\n  db:\n    image: postgres\n  web:\n    image: nginx\n    depends_on:\n      - db\n",
    )
    code = run_graph(_NS(str(a), str(b)))
    out = capsys.readouterr().out
    assert code == 0
    assert "[+] web" in out
    assert "-> db" in out
