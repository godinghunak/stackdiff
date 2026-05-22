"""End-to-end pipeline: parse -> diff -> validate -> filter -> sort -> annotate."""

from dataclasses import dataclass, field
from typing import Optional

from stackdiff.parser import load_compose_file, extract_services
from stackdiff.differ import diff_services
from stackdiff.reporter import build_report, DiffReport
from stackdiff.validator import validate_report, ValidationResult
from stackdiff.filter import FilterOptions, filter_report
from stackdiff.sorter import sort_report
from stackdiff.annotator import AnnotatedReport, annotate_report


@dataclass
class PipelineResult:
    report: DiffReport
    validation: ValidationResult
    annotated: AnnotatedReport
    has_changes: bool = field(init=False)

    def __post_init__(self) -> None:
        from stackdiff.reporter import has_changes as _has_changes
        self.has_changes = _has_changes(self.report)


def run_pipeline(
    file_a: str,
    file_b: str,
    filter_options: Optional[FilterOptions] = None,
) -> PipelineResult:
    """Run the full stackdiff pipeline and return a PipelineResult."""
    data_a = load_compose_file(file_a)
    data_b = load_compose_file(file_b)

    services_a = extract_services(data_a)
    services_b = extract_services(data_b)

    diffs = diff_services(services_a, services_b)
    report = build_report(services_a, services_b, diffs)

    from stackdiff.validator import validate_report
    validation = validate_report(report)

    if filter_options is not None:
        report = filter_report(report, filter_options)

    report = sort_report(report)
    annotated = annotate_report(report)

    return PipelineResult(report=report, validation=validation, annotated=annotated)
