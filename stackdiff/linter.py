"""Lint a DiffReport for common anti-patterns and suspicious changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from stackdiff.reporter import DiffReport
from stackdiff.differ import ServiceDiff


# Keys that are considered security-sensitive
_SENSITIVE_KEYS = frozenset(
    ["environment", "secrets", "cap_add", "cap_drop", "privileged", "user"]
)

# Keys that affect resource limits
_RESOURCE_KEYS = frozenset(["mem_limit", "memswap_limit", "cpus", "cpu_shares", "deploy"])


@dataclass
class LintWarning:
    service: str
    code: str
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.code}] {self.service}: {self.message}"


@dataclass
class LintResult:
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def add(self, warning: LintWarning) -> None:
        self.warnings.append(warning)

    def to_dict(self) -> dict:
        return {
            "clean": self.is_clean,
            "warnings": [
                {"service": w.service, "code": w.code, "message": w.message}
                for w in self.warnings
            ],
        }


def _lint_diff(name: str, diff: ServiceDiff, result: LintResult) -> None:
    changed_keys = set(diff.changed.keys())

    sensitive_hits = changed_keys & _SENSITIVE_KEYS
    for key in sorted(sensitive_hits):
        result.add(
            LintWarning(
                service=name,
                code="SENSITIVE_CHANGE",
                message=f"Security-sensitive key '{key}' was modified.",
            )
        )

    resource_hits = changed_keys & _RESOURCE_KEYS
    for key in sorted(resource_hits):
        result.add(
            LintWarning(
                service=name,
                code="RESOURCE_CHANGE",
                message=f"Resource-related key '{key}' was modified.",
            )
        )

    if diff.added:
        result.add(
            LintWarning(
                service=name,
                code="KEYS_ADDED",
                message=f"{len(diff.added)} key(s) added: {', '.join(sorted(diff.added))}.",
            )
        )


def lint_report(report: DiffReport) -> LintResult:
    """Run all lint checks against *report* and return a :class:`LintResult`."""
    result = LintResult()
    for name in sorted(report.added):
        result.add(
            LintWarning(service=name, code="SERVICE_ADDED", message="New service introduced.")
        )
    for name in sorted(report.removed):
        result.add(
            LintWarning(service=name, code="SERVICE_REMOVED", message="Existing service removed.")
        )
    for name, diff in sorted(report.changed.items()):
        _lint_diff(name, diff, result)
    return result
