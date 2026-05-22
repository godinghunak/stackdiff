"""Tests for stackdiff.cli."""

import os
import textwrap
import pytest

from stackdiff.cli import run


@pytest.fixture()
def compose_dir(tmp_path):
    """Return a helper that writes compose files into tmp_path."""

    def _write(filename, content):
        path = tmp_path / filename
        path.write_text(textwrap.dedent(content))
        return str(path)

    return _write


def test_cli_no_diff(compose_dir):
    base = compose_dir("base.yml", """
        version: '3'
        services:
          web:
            image: nginx:1.21
    """)
    target = compose_dir("target.yml", """
        version: '3'
        services:
          web:
            image: nginx:1.21
    """)
    exit_code = run([base, target])
    assert exit_code == 0


def test_cli_diff_no_exit_code_flag(compose_dir):
    base = compose_dir("base.yml", """
        version: '3'
        services:
          web:
            image: nginx:1.21
    """)
    target = compose_dir("target.yml", """
        version: '3'
        services:
          web:
            image: nginx:1.25
    """)
    exit_code = run([base, target])
    assert exit_code == 0


def test_cli_diff_with_exit_code_flag(compose_dir):
    base = compose_dir("base.yml", """
        version: '3'
        services:
          web:
            image: nginx:1.21
    """)
    target = compose_dir("target.yml", """
        version: '3'
        services:
          api:
            image: myapp:latest
    """)
    exit_code = run([base, target, "--exit-code"])
    assert exit_code == 1


def test_cli_missing_file_returns_2(compose_dir):
    existing = compose_dir("base.yml", """
        version: '3'
        services:
          web:
            image: nginx
    """)
    exit_code = run([existing, "/nonexistent/path/compose.yml"])
    assert exit_code == 2


def test_cli_color_flag_does_not_crash(compose_dir, capsys):
    base = compose_dir("base.yml", """
        version: '3'
        services:
          web:
            image: nginx:1.21
    """)
    target = compose_dir("target.yml", """
        version: '3'
        services:
          web:
            image: nginx:1.25
    """)
    exit_code = run([base, target, "--color"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "web" in captured.out
