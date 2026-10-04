from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict
from .attestation import canonical_json


@dataclass(frozen=True)
class EvidenceNode:
    evidence_id: str
    source_group: str
    parent_evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceGraph:
    nodes: tuple[EvidenceNode, ...]

    @classmethod
    def from_evidence(cls, evidence: list[Evidence]) -> "EvidenceGraph":
        nodes = tuple(
            EvidenceNode(
                evidence_id=item.evidence_id,
                source_group=item.source_group,
                parent_evidence_ids=tuple(sorted(item.parent_evidence_ids)),
            )
            for item in evidence
        )
        return cls(nodes=nodes)

    def independent_source_groups(self, evidence: list[Evidence]) -> set[str]:
        """Count source groups, not correlated signals, as independent support."""
        usable_ids = {
            item.evidence_id
            for item in evidence
            if item.status is SignalStatus.AVAILABLE
            and item.kind is EvidenceKind.VERDICT
            and item.verdict is not None
            and item.confidence is not None
        }
        return {
            node.source_group
            for node in self.nodes
            if node.evidence_id in usable_ids
        }

    def digest(self) -> str:
        payload = [
            {
                "evidence_id": node.evidence_id,
                "source_group": node.source_group,
                "parent_evidence_ids": list(node.parent_evidence_ids),
            }
            for node in sorted(self.nodes, key=lambda n: n.evidence_id)
        ]
        return hashlib.sha256(canonical_json(payload)).hexdigest()
