"""Serializes a DiffReport to JSON or YAML output formats."""

from __future__ import annotations

import json
from typing import Literal

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _YAML_AVAILABLE = False

from stackdiff.reporter import DiffReport

OutputFormat = Literal["json", "yaml"]


def serialize(report: DiffReport, fmt: OutputFormat = "json") -> str:
    """Serialize *report* to the requested string format.

    Parameters
    ----------
    report:
        The :class:`~stackdiff.reporter.DiffReport` to serialize.
    fmt:
        Either ``"json"`` (default) or ``"yaml"``.

    Raises
    ------
    ValueError
        If *fmt* is ``"yaml"`` and PyYAML is not installed, or if an
        unsupported format string is provided.
    """
    data = report.to_dict()

    if fmt == "json":
        return json.dumps(data, indent=2)

    if fmt == "yaml":
        if not _YAML_AVAILABLE:  # pragma: no cover
            raise ValueError(
                "PyYAML is required for YAML output. "
                "Install it with: pip install pyyaml"
            )
        return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)

    raise ValueError(f"Unsupported output format: {fmt!r}. Choose 'json' or 'yaml'.")
