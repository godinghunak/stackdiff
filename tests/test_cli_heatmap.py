"""Integration tests for the heatmap CLI sub-command."""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

import pytest

from stackdiff.cli_heatmap import build_heatmap_parser, run_heatmap, render_heatmap
from stackdiff.differ_heatmap import DiffHeatmap, HeatmapEntry


def _write(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content))
    return path


@pytest.fixture()
def compose_dir(tmp_path: Path):
    return tmp_path


class _NS:
    """Minimal argparse.Namespace stand-in."""
    def __init__(self, file_a: str, file_b: str, only=None):
        self.file_a = file_a
        self.file_b = file_b
        self.only = only


# --- render_heatmap ---

def test_render_heatmap_empty():
    output = render_heatmap(DiffHeatmap())
    assert "empty" in output.lower()


def test_render_heatmap_shows_service_name():
    heatmap = DiffHeatmap(entries=[
        HeatmapEntry(service="redis", change_count=3, change_types=["added", "changed"]),
    ])
    output = render_heatmap(heatmap)
    assert "redis" in output
    assert "3" in output


def test_render_heatmap_shows_change_types():
    heatmap = DiffHeatmap(entries=[
        HeatmapEntry(service="db", change_count=1, change_types=["removed"]),
    ])
    output = render_heatmap(heatmap)
    assert "removed" in output


# --- run_heatmap (integration) ---

def test_cli_heatmap_no_changes(compose_dir: Path, capsys):
    base = """
        version: '3'
        services:
          web:
            image: nginx
    """
    a = _write(compose_dir / "a.yml", base)
    b = _write(compose_dir / "b.yml", base)
    code = run_heatmap(_NS(str(a), str(b)))
    assert code == 0
    captured = capsys.readouterr()
    assert "empty" in captured.out.lower()


def test_cli_heatmap_with_changes(compose_dir: Path, capsys):
    a_text = """
        version: '3'
        services:
          api:
            image: myapp:1
    """
    b_text = """
        version: '3'
        services:
          api:
            image: myapp:2
            ports:
              - '8080:8080'
    """
    a = _write(compose_dir / "a.yml", a_text)
    b = _write(compose_dir / "b.yml", b_text)
    code = run_heatmap(_NS(str(a), str(b)))
    assert code == 0
    captured = capsys.readouterr()
    assert "api" in captured.out


def test_cli_heatmap_parser_registered():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_heatmap_parser(sub)
    args = parser.parse_args(["heatmap", "a.yml", "b.yml"])
    assert args.file_a == "a.yml"
    assert args.file_b == "b.yml"
    assert args.only is None
