"""Tests for stackdiff.cli_tagger."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from stackdiff.cli_tagger import run_tagger


def _write(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content))


@pytest.fixture()
def compose_dir(tmp_path: Path):
    return tmp_path


class _NS:
    def __init__(self, base, head, format="text", filter_tag=None):
        self.base = str(base)
        self.head = str(head)
        self.format = format
        self.filter_tag = filter_tag


def test_no_changes_prints_message(compose_dir, capsys):
    base = compose_dir / "base.yml"
    head = compose_dir / "head.yml"
    content = """\
        version: '3'
        services:
          web:
            image: nginx:1.24
    """
    _write(base, content)
    _write(head, content)
    rc = run_tagger(_NS(base, head))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No tagged" in out


def test_added_service_tagged(compose_dir, capsys):
    base = compose_dir / "base.yml"
    head = compose_dir / "head.yml"
    _write(base, "version: '3'\nservices:\n  web:\n    image: nginx\n")
    _write(head, "version: '3'\nservices:\n  web:\n    image: nginx\n  db:\n    image: postgres\n")
    rc = run_tagger(_NS(base, head))
    assert rc == 0
    out = capsys.readouterr().out
    assert "db" in out
    assert "added" in out


def test_json_output(compose_dir, capsys):
    base = compose_dir / "base.yml"
    head = compose_dir / "head.yml"
    _write(base, "version: '3'\nservices:\n  web:\n    image: nginx:1\n")
    _write(head, "version: '3'\nservices:\n  web:\n    image: nginx:2\n")
    rc = run_tagger(_NS(base, head, format="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "services" in data


def test_filter_tag_hides_unmatched(compose_dir, capsys):
    base = compose_dir / "base.yml"
    head = compose_dir / "head.yml"
    _write(base, "version: '3'\nservices:\n  web:\n    image: nginx:1\n")
    _write(
        head,
        "version: '3'\nservices:\n  web:\n    image: nginx:2\n  cache:\n    image: redis\n",
    )
    rc = run_tagger(_NS(base, head, filter_tag="added"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "cache" in out
    assert "web" not in out
