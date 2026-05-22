"""Tests for the parser and differ modules."""

import textwrap
from pathlib import Path

import pytest

from stackdiff.parser import ComposeParseError, extract_services, load_compose_file
from stackdiff.differ import diff_services


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_compose(tmp_path: Path, content: str, filename: str = "docker-compose.yml") -> Path:
    p = tmp_path / filename
    p.write_text(textwrap.dedent(content))
    return p


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

def test_load_compose_file_basic(tmp_path):
    f = write_compose(tmp_path, """
        services:
          web:
            image: nginx:latest
    """)
    data = load_compose_file(f)
    assert "services" in data


def test_load_compose_file_missing_raises(tmp_path):
    with pytest.raises(ComposeParseError, match="not found"):
        load_compose_file(tmp_path / "nonexistent.yml")


def test_load_compose_file_invalid_yaml(tmp_path):
    f = write_compose(tmp_path, "key: [unclosed")
    with pytest.raises(ComposeParseError, match="Invalid YAML"):
        load_compose_file(f)


def test_extract_services_empty(tmp_path):
    f = write_compose(tmp_path, "version: '3'\n")
    data = load_compose_file(f)
    assert extract_services(data) == {}


def test_extract_services_returns_dict(tmp_path):
    f = write_compose(tmp_path, """
        services:
          db:
            image: postgres:15
    """)
    services = extract_services(load_compose_file(f))
    assert "db" in services
    assert services["db"]["image"] == "postgres:15"


# ---------------------------------------------------------------------------
# Differ tests
# ---------------------------------------------------------------------------

def test_diff_added_service():
    old = {"web": {"image": "nginx"}}
    new = {"web": {"image": "nginx"}, "worker": {"image": "python:3.12"}}
    diffs = {d.name: d for d in diff_services(old, new)}
    assert diffs["worker"].status == "added"
    assert diffs["web"].status == "unchanged"


def test_diff_removed_service():
    old = {"web": {"image": "nginx"}, "cache": {"image": "redis"}}
    new = {"web": {"image": "nginx"}}
    diffs = {d.name: d for d in diff_services(old, new)}
    assert diffs["cache"].status == "removed"


def test_diff_changed_service():
    old = {"web": {"image": "nginx:1.24", "ports": ["80:80"]}}
    new = {"web": {"image": "nginx:1.25", "ports": ["80:80"]}}
    diffs = {d.name: d for d in diff_services(old, new)}
    assert diffs["web"].status == "changed"
    assert "image" in diffs["web"].changed_keys
    assert diffs["web"].changed_keys["image"] == ("nginx:1.24", "nginx:1.25")


def test_diff_key_added_and_removed():
    old = {"api": {"image": "myapp", "env_file": ".env"}}
    new = {"api": {"image": "myapp", "environment": ["DEBUG=1"]}}
    diffs = {d.name: d for d in diff_services(old, new)}
    assert "environment" in diffs["api"].added_keys
    assert "env_file" in diffs["api"].removed_keys
