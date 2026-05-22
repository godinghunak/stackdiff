"""Tests for stackdiff.validator."""

from __future__ import annotations

import pytest

from stackdiff.validator import (
    ValidationResult,
    ValidationWarning,
    validate_services,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _messages(result: ValidationResult) -> list[str]:
    return [w.message for w in result.warnings]


def _services(result: ValidationResult) -> list[str]:
    return [w.service for w in result.warnings]


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------

def test_validation_result_clean_when_empty():
    result = ValidationResult()
    assert result.is_clean


def test_validation_result_not_clean_after_add():
    result = ValidationResult()
    result.add("web", "some warning")
    assert not result.is_clean
    assert len(result.warnings) == 1


def test_validation_warning_str():
    w = ValidationWarning(service="db", message="missing image")
    assert str(w) == "[db] missing image"


# ---------------------------------------------------------------------------
# validate_services — happy paths
# ---------------------------------------------------------------------------

def test_valid_service_no_warnings():
    services = {"web": {"image": "nginx:latest", "restart": "always"}}
    result = validate_services(services)
    assert result.is_clean


def test_valid_service_with_build():
    services = {"app": {"build": ".", "ports": ["8080:80"]}}
    result = validate_services(services)
    assert result.is_clean


def test_empty_services_no_warnings():
    result = validate_services({})
    assert result.is_clean


# ---------------------------------------------------------------------------
# validate_services — missing image/build
# ---------------------------------------------------------------------------

def test_missing_image_and_build_warns():
    services = {"worker": {"command": "python worker.py"}}
    result = validate_services(services)
    messages = _messages(result)
    assert any("image" in m and "build" in m for m in messages)


# ---------------------------------------------------------------------------
# validate_services — restart policy
# ---------------------------------------------------------------------------

def test_invalid_restart_policy_warns():
    services = {"web": {"image": "nginx", "restart": "yes"}}
    result = validate_services(services)
    messages = _messages(result)
    assert any("restart" in m for m in messages)


def test_valid_restart_policies_no_warning():
    for policy in ("no", "always", "on-failure", "unless-stopped"):
        services = {"svc": {"image": "alpine", "restart": policy}}
        assert validate_services(services).is_clean, f"policy '{policy}' should be valid"


# ---------------------------------------------------------------------------
# validate_services — unknown keys
# ---------------------------------------------------------------------------

def test_unknown_key_warns():
    services = {"web": {"image": "nginx", "foo_bar": "baz"}}
    result = validate_services(services)
    messages = _messages(result)
    assert any("foo_bar" in m for m in messages)


def test_known_keys_no_unknown_warning():
    services = {"web": {"image": "nginx", "environment": {"ENV": "val"}}}
    result = validate_services(services)
    assert not any("unknown key" in m for m in _messages(result))


# ---------------------------------------------------------------------------
# validate_services — non-mapping definition
# ---------------------------------------------------------------------------

def test_non_mapping_definition_warns():
    services = {"broken": None}
    result = validate_services(services)
    messages = _messages(result)
    assert any("not a mapping" in m for m in messages)


# ---------------------------------------------------------------------------
# validate_services — service name attached to warnings
# ---------------------------------------------------------------------------

def test_warning_carries_correct_service_name():
    services = {"myservice": {"command": "echo hi"}}  # no image or build
    result = validate_services(services)
    assert "myservice" in _services(result)
