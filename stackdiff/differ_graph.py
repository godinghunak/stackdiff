"""Build a dependency graph from a DiffReport, showing service relationships."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from stackdiff.reporter import DiffReport


@dataclass
class GraphNode:
    name: str
    change_type: str  # 'added', 'removed', 'changed', 'unchanged'
    depends_on: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "change_type": self.change_type,
            "depends_on": self.depends_on,
        }


@dataclass
class DiffGraph:
    nodes: Dict[str, GraphNode] = field(default_factory=dict)

    def all_service_names(self) -> List[str]:
        return sorted(self.nodes.keys())

    def neighbours(self, name: str) -> List[str]:
        node = self.nodes.get(name)
        return node.depends_on if node else []

    def affected_by(self, name: str) -> List[str]:
        """Return services that depend on *name* (reverse edges)."""
        return [
            n for n, node in self.nodes.items() if name in node.depends_on
        ]

    def to_dict(self) -> dict:
        return {name: node.to_dict() for name, node in self.nodes.items()}


def _change_type_for(name: str, report: DiffReport) -> str:
    if name in report.added:
        return "added"
    if name in report.removed:
        return "removed"
    if name in report.changed:
        return "changed"
    return "unchanged"


def build_graph(report: DiffReport, raw_services: Dict[str, dict]) -> DiffGraph:
    """Build a DiffGraph from a report and the raw service definitions.

    *raw_services* should be the merged set of service keys from both compose
    files so that dependency edges can be resolved even for removed services.
    """
    graph = DiffGraph()
    for name, definition in raw_services.items():
        depends_on: List[str] = []
        raw_deps = definition.get("depends_on", [])
        if isinstance(raw_deps, list):
            depends_on = [d for d in raw_deps if isinstance(d, str)]
        elif isinstance(raw_deps, dict):
            depends_on = list(raw_deps.keys())
        graph.nodes[name] = GraphNode(
            name=name,
            change_type=_change_type_for(name, report),
            depends_on=depends_on,
        )
    return graph
