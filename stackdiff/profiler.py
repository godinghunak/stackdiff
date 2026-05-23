"""Profiles a DiffReport to produce per-service complexity scores.

A service's complexity score is a simple integer reflecting how many
distinct fields were added, removed, or changed across its diff.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from stackdiff.reporter import DiffReport
from stackdiff.differ import ServiceDiff


@dataclass
class ServiceProfile:
    service_name: str
    added_fields: int = 0
    removed_fields: int = 0
    changed_fields: int = 0

    @property
    def complexity_score(self) -> int:
        """Total number of field-level changes for this service."""
        return self.added_fields + self.removed_fields + self.changed_fields

    def to_dict(self) -> dict:
        return {
            "service": self.service_name,
            "added_fields": self.added_fields,
            "removed_fields": self.removed_fields,
            "changed_fields": self.changed_fields,
            "complexity_score": self.complexity_score,
        }


@dataclass
class ProfileReport:
    profiles: List[ServiceProfile] = field(default_factory=list)

    @property
    def most_complex(self) -> ServiceProfile | None:
        if not self.profiles:
            return None
        return max(self.profiles, key=lambda p: p.complexity_score)

    def to_dict(self) -> dict:
        return {
            "profiles": [p.to_dict() for p in self.profiles],
            "most_complex": self.most_complex.service_name if self.most_complex else None,
        }


def _profile_diff(name: str, diff: ServiceDiff) -> ServiceProfile:
    profile = ServiceProfile(service_name=name)
    if diff.added is not None:
        profile.added_fields = len(diff.added) if isinstance(diff.added, dict) else 1
    if diff.removed is not None:
        profile.removed_fields = len(diff.removed) if isinstance(diff.removed, dict) else 1
    if diff.changed:
        profile.changed_fields = len(diff.changed)
    return profile


def profile_report(report: DiffReport) -> ProfileReport:
    """Build a ProfileReport from a DiffReport."""
    profiles: List[ServiceProfile] = []

    for name in report.added:
        profiles.append(ServiceProfile(service_name=name, added_fields=1))

    for name in report.removed:
        profiles.append(ServiceProfile(service_name=name, removed_fields=1))

    for name, diff in report.changed.items():
        profiles.append(_profile_diff(name, diff))

    profiles.sort(key=lambda p: p.complexity_score, reverse=True)
    return ProfileReport(profiles=profiles)
