"""Generate a human-readable changelog from a DiffReport."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from stackdiff.reporter import DiffReport


@dataclass
class ChangelogEntry:
    """A single versioned changelog entry."""

    version: str
    timestamp: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
        }


def build_changelog_entry(
    report: DiffReport,
    version: str,
    timestamp: Optional[str] = None,
) -> ChangelogEntry:
    """Build a ChangelogEntry from a DiffReport."""
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    added = sorted(report.added)
    removed = sorted(report.removed)
    changed = sorted(report.changed.keys())
    return ChangelogEntry(
        version=version,
        timestamp=ts,
        added=added,
        removed=removed,
        changed=changed,
    )


def render_changelog(entry: ChangelogEntry) -> str:
    """Render a ChangelogEntry as a Markdown-style string."""
    lines: List[str] = []
    lines.append(f"## [{entry.version}] — {entry.timestamp}")
    if entry.is_empty():
        lines.append("")
        lines.append("_No changes detected._")
        return "\n".join(lines)
    if entry.added:
        lines.append("")
        lines.append("### Added")
        for svc in entry.added:
            lines.append(f"- `{svc}`")
    if entry.removed:
        lines.append("")
        lines.append("### Removed")
        for svc in entry.removed:
            lines.append(f"- `{svc}`")
    if entry.changed:
        lines.append("")
        lines.append("### Changed")
        for svc in entry.changed:
            lines.append(f"- `{svc}`")
    return "\n".join(lines)
