from __future__ import annotations

from .contracts import Evidence


def validate_cctv_evidence_lineage(evidence: list[Evidence]) -> None:
    """Validate CCTV/face evidence does not masquerade as identity evidence."""
    by_id = {item.evidence_id: item for item in evidence if item.evidence_id}

    for item in evidence:
        if not item.signal.startswith(("cctv.", "face.")):
            continue

        if item.kind.value != "fact":
            raise ValueError("CCTV and face visibility evidence must remain factual evidence")

        identity_status = item.details.get("identity_status") if isinstance(item.details, dict) else None
        if identity_status not in (None, "UNVERIFIED"):
            raise ValueError("CCTV visibility evidence cannot assert verified identity")

        if isinstance(item.details, dict) and item.details.get("reconstruction_allowed") is True:
            raise ValueError("Face reconstruction cannot be enabled as verification evidence")

        for parent_id in item.parent_evidence_ids:
            parent = by_id.get(parent_id)
            if parent is None:
                raise ValueError("CCTV evidence references missing parent evidence")
            if parent_id == item.evidence_id:
                raise ValueError("CCTV evidence cannot reference itself")

            # Face-visibility observations may depend on media/frame facts, but they
            # must not inherit identity claims from another face-comparison signal.
            if parent.signal.startswith(("cctv.", "face.")) and parent.kind.value != "fact":
                raise ValueError("CCTV evidence lineage cannot inherit a non-factual face signal")


def cctv_independence_group(evidence: Evidence) -> str | None:
    if not evidence.signal.startswith(("cctv.", "face.")):
        return None
    return evidence.source_group or "cctv_face"
