"""Validates Docker Compose service definitions for common issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

KNOWN_TOP_LEVEL_KEYS = {
    "image", "build", "command", "entrypoint", "environment", "env_file",
    "ports", "volumes", "networks", "depends_on", "restart", "labels",
    "healthcheck", "deploy", "secrets", "configs", "expose", "user",
    "working_dir", "hostname", "extra_hosts", "dns", "cap_add", "cap_drop",
    "privileged", "read_only", "stdin_open", "tty", "logging", "ulimits",
    "stop_grace_period", "stop_signal", "platform", "profiles", "mem_limit",
    "cpus",
}


@dataclass
class ValidationWarning:
    service: str
    message: str

    def __str__(self) -> str:
        return f"[{self.service}] {self.message}"


@dataclass
class ValidationResult:
    warnings: list[ValidationWarning] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def add(self, service: str, message: str) -> None:
        self.warnings.append(ValidationWarning(service=service, message=message))


def _check_service(name: str, definition: dict[str, Any], result: ValidationResult) -> None:
    """Run all checks for a single service definition."""
    if not isinstance(definition, dict):
        result.add(name, "service definition is not a mapping")
        return

    if "image" not in definition and "build" not in definition:
        result.add(name, "missing both 'image' and 'build'; service may not start")

    ports = definition.get("ports", [])
    if isinstance(ports, list):
        for port in ports:
            port_str = str(port)
            if port_str.startswith("0.0.0.0:") or ":" not in port_str:
                result.add(name, f"port '{port}' binds to all interfaces or lacks host mapping")

    restart = definition.get("restart")
    if restart is not None and restart not in (
        "no", "always", "on-failure", "unless-stopped"
    ):
        result.add(name, f"unrecognised restart policy '{restart}'")

    unknown_keys = set(definition.keys()) - KNOWN_TOP_LEVEL_KEYS
    for key in sorted(unknown_keys):
        result.add(name, f"unknown key '{key}'")


def validate_services(services: dict[str, Any]) -> ValidationResult:
    """Validate all services in a parsed Compose services dict."""
    result = ValidationResult()
    for name, definition in services.items():
        _check_service(name, definition or {}, result)
    return result
