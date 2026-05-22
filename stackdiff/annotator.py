"""Annotates a DiffReport with human-readable change descriptions per service."""

from dataclasses import dataclass, field
from typing import Dict, List

from stackdiff.reporter import DiffReport
from stackdiff.differ import ServiceDiff


@dataclass
class ServiceAnnotation:
    """Human-readable annotations for a single service's diff."""

    service: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"service": self.service, "status": self.status, "notes": self.notes}


@dataclass
class AnnotatedReport:
    """A DiffReport enriched with per-service annotations."""

    annotations: Dict[str, ServiceAnnotation] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {k: v.to_dict() for k, v in self.annotations.items()}


def _notes_for_diff(diff: ServiceDiff) -> List[str]:
    notes: List[str] = []
    if diff.image_changed:
        old = diff.old.get("image", "<none>") if diff.old else "<none>"
        new = diff.new.get("image", "<none>") if diff.new else "<none>"
        notes.append(f"image changed: {old!r} -> {new!r}")
    for key in diff.added_keys:
        notes.append(f"key added: {key!r}")
    for key in diff.removed_keys:
        notes.append(f"key removed: {key!r}")
    for key in diff.changed_keys:
        old_val = diff.old.get(key) if diff.old else None
        new_val = diff.new.get(key) if diff.new else None
        notes.append(f"key changed: {key!r} ({old_val!r} -> {new_val!r})")
    return notes


def annotate_report(report: DiffReport) -> AnnotatedReport:
    """Build an AnnotatedReport from a DiffReport."""
    annotated = AnnotatedReport()

    for name in report.added:
        annotated.annotations[name] = ServiceAnnotation(
            service=name, status="added", notes=["service is new"]
        )

    for name in report.removed:
        annotated.annotations[name] = ServiceAnnotation(
            service=name, status="removed", notes=["service was removed"]
        )

    for name, diff in report.changed.items():
        notes = _notes_for_diff(diff)
        annotated.annotations[name] = ServiceAnnotation(
            service=name, status="changed", notes=notes
        )

    return annotated
