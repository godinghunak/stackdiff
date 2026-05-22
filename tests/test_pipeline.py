"""Integration tests for stackdiff.pipeline.run_pipeline."""

import textwrap
from pathlib import Path

import pytest

from stackdiff.pipeline import run_pipeline


@pytest.fixture()
def compose_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(textwrap.dedent(content))
    return p


def test_pipeline_no_changes(compose_dir):
    a = _write(compose_dir, "a.yml", """
        services:
          web:
            image: nginx:1.25
    """)
    report = run_pipeline(a, a)
    assert report.added == []
    assert report.removed == []
    assert report.changed == {}


def test_pipeline_detects_added_service(compose_dir):
    a = _write(compose_dir, "a.yml", """
        services:
          web:
            image: nginx:1.25
    """)
    b = _write(compose_dir, "b.yml", """
        services:
          web:
            image: nginx:1.25
          worker:
            image: myapp:latest
    """)
    report = run_pipeline(a, b)
    assert "worker" in report.added
    assert report.removed == []


def test_pipeline_filter_excludes_added(compose_dir):
    a = _write(compose_dir, "a.yml", """
        services:
          web:
            image: nginx:1.25
    """)
    b = _write(compose_dir, "b.yml", """
        services:
          web:
            image: nginx:1.25
          worker:
            image: myapp:latest
    """)
    report = run_pipeline(a, b, include_added=False)
    assert report.added == []


def test_pipeline_service_name_filter(compose_dir):
    a = _write(compose_dir, "a.yml", """
        services:
          web:
            image: nginx:1.24
          db:
            image: postgres:14
    """)
    b = _write(compose_dir, "b.yml", """
        services:
          web:
            image: nginx:1.25
          db:
            image: postgres:15
    """)
    report = run_pipeline(a, b, service_names={"web"})
    assert "web" in report.changed
    assert "db" not in report.changed


def test_pipeline_output_is_sorted(compose_dir):
    a = _write(compose_dir, "a.yml", """
        services:
          zz:
            image: img:1
    """)
    b = _write(compose_dir, "b.yml", """
        services:
          zz:
            image: img:1
          aa:
            image: img:2
          mm:
            image: img:3
    """)
    report = run_pipeline(a, b)
    assert report.added == sorted(report.added)
