"""Evidence graph primitives for conservative multimodal fusion.

The graph records provenance between evidence items and prevents derived or
correlated signals from being counted as independent confirmation.
"""
from __future__ import annotations

from dataclasses import dataclass
from .contracts import Evidence, EvidenceKind, SignalStatus


@dataclass(frozen=True)
class EvidenceGraphAnalysis:
    evidence_ids: tuple[str, ...]
    root_source_groups: tuple[str, ...]
    contradictions: tuple[tuple[str, str], ...]
    usable_count: int

    @property
    def independent_sources(self) -> int:
        return len(self.root_source_groups)


def analyze_evidence_graph(evidence: list[Evidence]) -> EvidenceGraphAnalysis:
    """Analyze provenance without inventing evidence or upgrading uncertainty."""
    by_id: dict[str, Evidence] = {}
    for item in evidence:
        if item.evidence_id:
            if item.evidence_id in by_id:
                raise ValueError(f"duplicate evidence_id: {item.evidence_id}")
            by_id[item.evidence_id] = item

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(evidence_id: str) -> None:
        if evidence_id in visiting:
            raise ValueError("evidence graph contains a cycle")
        if evidence_id in visited:
            return
        visiting.add(evidence_id)
        for parent_id in by_id[evidence_id].parent_evidence_ids:
            if parent_id not in by_id:
                raise ValueError(f"unknown parent evidence_id: {parent_id}")
            visit(parent_id)
        visiting.remove(evidence_id)
        visited.add(evidence_id)

    for evidence_id in by_id:
        visit(evidence_id)

    usable = [
        item for item in evidence
        if item.status is SignalStatus.AVAILABLE
        and item.kind in {EvidenceKind.FACT, EvidenceKind.VERDICT}
    ]

    def root_groups(item: Evidence, seen: set[str] | None = None) -> set[str]:
        seen = set() if seen is None else seen
        if item.evidence_id in seen:
            return set()
        seen.add(item.evidence_id)
        if not item.parent_evidence_ids:
            return {item.source_group or item.signal}
        groups: set[str] = set()
        for parent_id in item.parent_evidence_ids:
            groups.update(root_groups(by_id[parent_id], seen))
        return groups

    roots: set[str] = set()
    for item in usable:
        roots.update(root_groups(item))

    contradictions: set[tuple[str, str]] = set()
    by_signal: dict[str, set[str]] = {}
    for item in usable:
        if item.verdict is not None:
            by_signal.setdefault(item.signal, set()).add(item.verdict.value)
    for signal, verdicts in by_signal.items():
        if len(verdicts) > 1:
            ordered = tuple(sorted(verdicts))
            contradictions.add((signal, " vs ".join(ordered)))

    return EvidenceGraphAnalysis(
        evidence_ids=tuple(item.evidence_id for item in evidence if item.evidence_id),
        root_source_groups=tuple(sorted(roots)),
        contradictions=tuple(sorted(contradictions)),
        usable_count=len(usable),
    )
