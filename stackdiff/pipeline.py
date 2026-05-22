"""High-level pipeline that wires parser -> differ -> reporter -> filter -> sort."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Set

from stackdiff.parser import load_compose_file, extract_services
from stackdiff.differ import diff_services
from stackdiff.reporter import DiffReport, build_report
from stackdiff.filter import FilterOptions, filter_report
from stackdiff.sorter import sort_report


def run_pipeline(
    path_a: Path,
    path_b: Path,
    include_added: bool = True,
    include_removed: bool = True,
    include_changed: bool = True,
    service_names: Optional[Set[str]] = None,
) -> DiffReport:
    """Parse two Compose files and return a filtered, sorted DiffReport."""
    data_a = load_compose_file(path_a)
    data_b = load_compose_file(path_b)

    services_a = extract_services(data_a)
    services_b = extract_services(data_b)

    diffs = diff_services(services_a, services_b)
    report = build_report(diffs)

    options = FilterOptions(
        include_added=include_added,
        include_removed=include_removed,
        include_changed=include_changed,
        service_names=service_names,
    )
    report = filter_report(report, options)
    report = sort_report(report)
    return report
