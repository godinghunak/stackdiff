"""Exports a DiffReport to various file-based formats."""

from __future__ import annotations

import json
import pathlib
from typing import Literal

from stackdiff.reporter import DiffReport
from stackdiff.serializer import serialize
from stackdiff.summarizer import render_summary

ExportFormat = Literal["json", "text"]


class ExportError(Exception):
    """Raised when an export operation fails."""


def export_report(
    report: DiffReport,
    dest: pathlib.Path,
    fmt: ExportFormat = "json",
) -> None:
    """Write *report* to *dest* in the requested format.

    Parameters
    ----------
    report:
        The diff report to export.
    dest:
        Destination file path.  Parent directories must already exist.
    fmt:
        ``'json'`` (default) or ``'text'`` for a plain-text summary.

    Raises
    ------
    ExportError
        If the format is unsupported or the file cannot be written.
    """
    if fmt == "json":
        payload = json.dumps(serialize(report), indent=2)
    elif fmt == "text":
        payload = render_summary(report)
    else:
        raise ExportError(f"Unsupported export format: {fmt!r}")

    try:
        dest.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"Failed to write export file {dest}: {exc}") from exc


def detect_format(dest: pathlib.Path) -> ExportFormat:
    """Infer an ExportFormat from *dest*'s file extension.

    Falls back to ``'text'`` for unknown extensions.
    """
    suffix = dest.suffix.lower()
    if suffix == ".json":
        return "json"
    return "text"
