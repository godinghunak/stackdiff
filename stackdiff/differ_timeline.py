"""Timeline tracking: record when services changed across multiple diffs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from stackdiff.reporter import DiffReport


@dataclass
class TimelineEvent:
    timestamp: str
    added: List[str]
    removed: List[str]
    changed: List[str]

    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
        }


@dataclass
class DiffTimeline:
    events: List[TimelineEvent] = field(default_factory=list)

    def append(self, event: TimelineEvent) -> None:
        self.events.append(event)

    def services_ever_changed(self) -> List[str]:
        seen: Dict[str, None] = {}
        for ev in self.events:
            for name in ev.added + ev.removed + ev.changed:
                seen[name] = None
        return list(seen.keys())

    def to_dict(self) -> dict:
        return {"events": [e.to_dict() for e in self.events]}


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def build_timeline_event(
    report: DiffReport,
    timestamp: Optional[str] = None,
) -> TimelineEvent:
    """Convert a DiffReport snapshot into a TimelineEvent."""
    ts = timestamp or _utc_now()
    return TimelineEvent(
        timestamp=ts,
        added=list(report.added),
        removed=list(report.removed),
        changed=list(report.changed.keys()),
    )


def record_event(
    timeline: DiffTimeline,
    report: DiffReport,
    timestamp: Optional[str] = None,
) -> TimelineEvent:
    """Build an event from *report* and append it to *timeline*."""
    event = build_timeline_event(report, timestamp=timestamp)
    timeline.append(event)
    return event
