"""Tests for stackdiff.linter."""
from __future__ import annotations

import pytest

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport
from stackdiff.linter import LintWarning, LintResult, lint_report


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_report(
    added=None,
    removed=None,
    changed=None,
) -> DiffReport:
    return DiffReport(
        added=list(added or []),
        removed=list(removed or []),
        changed=dict(changed or {}),
    )


def _make_diff(
    added=None,
    removed=None,
    changed=None,
) -> ServiceDiff:
    return ServiceDiff(
        added=dict(added or {}),
        removed=dict(removed or {}),
        changed=dict(changed or {}),
    )


# ---------------------------------------------------------------------------
# LintResult unit tests
# ---------------------------------------------------------------------------

def test_lint_result_clean_when_empty():
    result = LintResult()
    assert result.is_clean is True


def test_lint_result_not_clean_after_add():
    result = LintResult()
    result.add(LintWarning(service="svc", code="X", message="msg"))
    assert result.is_clean is False


def test_lint_result_to_dict_structure():
    result = LintResult()
    result.add(LintWarning(service="web", code="SERVICE_ADDED", message="New service."))
    d = result.to_dict()
    assert d["clean"] is False
    assert len(d["warnings"]) == 1
    assert d["warnings"][0]["code"] == "SERVICE_ADDED"


# ---------------------------------------------------------------------------
# lint_report integration tests
# ---------------------------------------------------------------------------

def test_lint_report_empty_is_clean():
    report = _make_report()
    result = lint_report(report)
    assert result.is_clean


def test_lint_report_added_service_raises_warning():
    report = _make_report(added=["newdb"])
    result = lint_report(report)
    codes = [w.code for w in result.warnings]
    assert "SERVICE_ADDED" in codes
    assert any(w.service == "newdb" for w in result.warnings)


def test_lint_report_removed_service_raises_warning():
    report = _make_report(removed=["cache"])
    result = lint_report(report)
    codes = [w.code for w in result.warnings]
    assert "SERVICE_REMOVED" in codes


def test_lint_report_sensitive_key_change():
    diff = _make_diff(changed={"environment": ("OLD", "NEW")})
    report = _make_report(changed={"api": diff})
    result = lint_report(report)
    codes = [w.code for w in result.warnings]
    assert "SENSITIVE_CHANGE" in codes
    assert any("environment" in w.message for w in result.warnings)


def test_lint_report_resource_key_change():
    diff = _make_diff(changed={"mem_limit": ("256m", "512m")})
    report = _make_report(changed={"worker": diff})
    result = lint_report(report)
    codes = [w.code for w in result.warnings]
    assert "RESOURCE_CHANGE" in codes


def test_lint_report_keys_added_warning():
    diff = _make_diff(added={"logging": {"driver": "json-file"}})
    report = _make_report(changed={"web": diff})
    result = lint_report(report)
    codes = [w.code for w in result.warnings]
    assert "KEYS_ADDED" in codes


def test_lint_report_multiple_warnings_for_same_service():
    diff = _make_diff(
        changed={"environment": ("a", "b"), "mem_limit": ("128m", "256m")},
    )
    report = _make_report(changed={"app": diff})
    result = lint_report(report)
    service_warnings = [w for w in result.warnings if w.service == "app"]
    assert len(service_warnings) >= 2
