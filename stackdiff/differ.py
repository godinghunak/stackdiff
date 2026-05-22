"""Differ module — computes service-level differences between two Compose files."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceDiff:
    """Holds the diff result for a single service."""

    name: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    added_keys: list[str] = field(default_factory=list)
    removed_keys: list[str] = field(default_factory=list)
    changed_keys: dict[str, tuple[Any, Any]] = field(default_factory=dict)


def _diff_service(
    name: str, old_def: dict | None, new_def: dict | None
) -> ServiceDiff:
    """Produce a ServiceDiff for a single service."""
    if old_def is None:
        return ServiceDiff(name=name, status="added")
    if new_def is None:
        return ServiceDiff(name=name, status="removed")

    old_def = old_def or {}
    new_def = new_def or {}

    old_keys = set(old_def.keys())
    new_keys = set(new_def.keys())

    added_keys = sorted(new_keys - old_keys)
    removed_keys = sorted(old_keys - new_keys)
    changed_keys = {
        k: (old_def[k], new_def[k])
        for k in old_keys & new_keys
        if old_def[k] != new_def[k]
    }

    status = "unchanged" if not (added_keys or removed_keys or changed_keys) else "changed"
    return ServiceDiff(
        name=name,
        status=status,
        added_keys=added_keys,
        removed_keys=removed_keys,
        changed_keys=changed_keys,
    )


def diff_services(
    old_services: dict[str, dict],
    new_services: dict[str, dict],
) -> list[ServiceDiff]:
    """Compare two service dicts and return a list of ServiceDiff objects.

    Args:
        old_services: Services from the base Compose file.
        new_services: Services from the target Compose file.

    Returns:
        Sorted list of ServiceDiff, one entry per unique service name.
    """
    all_names = sorted(set(old_services) | set(new_services))
    return [
        _diff_service(name, old_services.get(name), new_services.get(name))
        for name in all_names
    ]
