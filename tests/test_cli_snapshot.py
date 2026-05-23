"""Integration tests for the snapshot CLI sub-commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackdiff.cli_snapshot import run_snapshot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


SIMPLE_A = """
services:
  web:
    image: nginx:1.25
  db:
    image: postgres:15
"""

SIMPLE_B = """
services:
  web:
    image: nginx:1.26
  cache:
    image: redis:7
"""


@pytest.fixture()
def compose_dir(tmp_path: Path):
    a = _write(tmp_path / "a.yml", SIMPLE_A)
    b = _write(tmp_path / "b.yml", SIMPLE_B)
    return tmp_path, a, b


class _NS:
    """Minimal argparse.Namespace stand-in."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------

def test_save_snapshot_returns_zero(compose_dir):
    tmp_path, a, b = compose_dir
    dest = tmp_path / "snap.json"
    args = _NS(snap_cmd="save", file_a=str(a), file_b=str(b), output=str(dest))
    assert run_snapshot(args) == 0
    assert dest.exists()


def test_save_snapshot_json_has_expected_keys(compose_dir):
    tmp_path, a, b = compose_dir
    dest = tmp_path / "snap.json"
    args = _NS(snap_cmd="save", file_a=str(a), file_b=str(b), output=str(dest))
    run_snapshot(args)
    data = json.loads(dest.read_text())
    assert "added" in data
    assert "removed" in data
    assert "changed" in data


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------

def test_compare_against_own_snapshot_no_regression(compose_dir, capsys):
    tmp_path, a, b = compose_dir
    snap = tmp_path / "snap.json"
    save_args = _NS(snap_cmd="save", file_a=str(a), file_b=str(b), output=str(snap))
    run_snapshot(save_args)

    cmp_args = _NS(
        snap_cmd="compare",
        file_a=str(a),
        file_b=str(b),
        snapshot=str(snap),
        fail_on_regression=True,
    )
    code = run_snapshot(cmp_args)
    assert code == 0


def test_compare_missing_snapshot_returns_zero_without_flag(compose_dir):
    tmp_path, a, b = compose_dir
    args = _NS(
        snap_cmd="compare",
        file_a=str(a),
        file_b=str(b),
        snapshot=str(tmp_path / "missing.json"),
        fail_on_regression=False,
    )
    assert run_snapshot(args) == 0


def test_compare_regression_exits_one_with_flag(compose_dir, tmp_path):
    tmp_path2, a, b = compose_dir
    # Snapshot from identical files (no diff)
    same = _write(tmp_path / "same.yml", SIMPLE_A)
    snap = tmp_path / "snap.json"
    save_args = _NS(snap_cmd="save", file_a=str(same), file_b=str(same), output=str(snap))
    run_snapshot(save_args)

    # Now compare a diff that has new changes against the empty snapshot
    cmp_args = _NS(
        snap_cmd="compare",
        file_a=str(a),
        file_b=str(b),
        snapshot=str(snap),
        fail_on_regression=True,
    )
    code = run_snapshot(cmp_args)
    assert code == 1
