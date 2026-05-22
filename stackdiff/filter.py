"""Filter services from a DiffReport based on criteria."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set

from stackdiff.reporter import DiffReport


@dataclass
class FilterOptions:
    """Options controlling which services appear in filtered output."""

    include_added: bool = True
    include_removed: bool = True
    include_changed: bool = True
    service_names: Optional[Set[str]] = field(default=None)


def filter_report(report: DiffReport, options: FilterOptions) -> DiffReport:
    """Return a new DiffReport containing only the services that match *options*."""
    added = report.added if options.include_added else []
    removed = report.removed if options.include_removed else []
    changed = report.changed if options.include_changed else []

    if options.service_names is not None:
        names = options.service_names
        added = [s for s in added if s in names]
        removed = [s for s in removed if s in names]
        changed = {k: v for k, v in changed.items() if k in names}
    else:
        changed = dict(changed)

    return DiffReport(
        added=list(added),
        removed=list(removed),
        changed=changed,
    )
