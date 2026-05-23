"""Assigns semantic tags to service diffs for categorisation and filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from stackdiff.differ import ServiceDiff
from stackdiff.reporter import DiffReport

# Canonical tag constants
TAG_ADDED = "added"
TAG_REMOVED = "removed"
TAG_IMAGE_CHANGE = "image-change"
TAG_PORT_CHANGE = "port-change"
TAG_ENV_CHANGE = "env-change"
TAG_VOLUME_CHANGE = "volume-change"
TAG_NETWORK_CHANGE = "network-change"
TAG_RESOURCE_CHANGE = "resource-change"
TAG_CONFIG_CHANGE = "config-change"


@dataclass
class TaggedService:
    name: str
    tags: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict:
        return {"name": self.name, "tags": sorted(self.tags)}


@dataclass
class TagReport:
    services: List[TaggedService] = field(default_factory=list)

    def all_tags(self) -> Set[str]:
        result: Set[str] = set()
        for s in self.services:
            result |= s.tags
        return result

    def services_with_tag(self, tag: str) -> List[str]:
        return [s.name for s in self.services if tag in s.tags]

    def to_dict(self) -> Dict:
        return {"services": [s.to_dict() for s in self.services]}


def _tags_for_diff(diff: ServiceDiff) -> Set[str]:
    tags: Set[str] = set()
    if diff.added:
        tags.add(TAG_ADDED)
        return tags
    if diff.removed:
        tags.add(TAG_REMOVED)
        return tags
    changed_keys = {k for k, _ in diff.changes}
    if "image" in changed_keys:
        tags.add(TAG_IMAGE_CHANGE)
    if any(k.startswith("ports") for k in changed_keys):
        tags.add(TAG_PORT_CHANGE)
    if any(k.startswith("environment") for k in changed_keys):
        tags.add(TAG_ENV_CHANGE)
    if any(k.startswith("volumes") for k in changed_keys):
        tags.add(TAG_VOLUME_CHANGE)
    if any(k.startswith("networks") for k in changed_keys):
        tags.add(TAG_NETWORK_CHANGE)
    if any(k in changed_keys for k in ("deploy", "resources", "mem_limit", "cpus")):
        tags.add(TAG_RESOURCE_CHANGE)
    if changed_keys - {TAG_IMAGE_CHANGE}:
        tags.add(TAG_CONFIG_CHANGE)
    return tags


def tag_report(report: DiffReport) -> TagReport:
    """Produce a TagReport from a DiffReport."""
    tagged: List[TaggedService] = []
    for diff in report.diffs:
        tags = _tags_for_diff(diff)
        if tags:
            tagged.append(TaggedService(name=diff.service, tags=tags))
    return TagReport(services=tagged)
