from __future__ import annotations

from .contracts import Evidence, EvidenceKind, SignalStatus
from .cctv_master import CCTVMasterAssessment
from .face_comparison import FaceVisibilityComparison


def cctv_master_to_evidence(
    assessment: CCTVMasterAssessment,
    *,
    evidence_id: str,
    source_group: str = "cctv_face",
) -> Evidence:
    if not evidence_id:
        raise ValueError("evidence_id must not be empty")

    if assessment.status.value == "supported":
        status = SignalStatus.AVAILABLE
        summary = (
            f"CCTV face visibility is {assessment.face_visibility}; "
            f"temporal consistency is {assessment.temporal_consistency}."
        )
    elif assessment.status.value == "conflicting":
        status = SignalStatus.AVAILABLE
        summary = "CCTV face visibility evidence is conflicting across analyzed observations."
    else:
        status = SignalStatus.UNAVAILABLE
        summary = "CCTV face visibility evidence is insufficient for a reliable conclusion."

    return Evidence(
        evidence_id=evidence_id,
        source_group=source_group,
        signal="cctv.face_visibility",
        status=status,
        kind=EvidenceKind.FACT,
        summary=summary,
        details={
            "visibility": assessment.face_visibility,
            "visible_fraction": assessment.visible_fraction,
            "covering": assessment.covering,
            "temporal_consistency": assessment.temporal_consistency,
            "evidence_strength": assessment.evidence_strength,
            "identity_status": assessment.identity_status,
            "reconstruction_allowed": assessment.reconstruction_allowed,
            "limitations": list(assessment.limitations),
        },
    )


def face_comparison_to_evidence(
    comparison: FaceVisibilityComparison,
    *,
    evidence_id: str,
    source_group: str = "face_comparison",
) -> Evidence:
    if not evidence_id:
        raise ValueError("evidence_id must not be empty")

    status = (
        SignalStatus.AVAILABLE
        if comparison.status.value != "insufficient"
        else SignalStatus.UNAVAILABLE
    )

    summary = (
        f"Observable face visibility comparison is {comparison.status.value}; "
        f"visibility delta={comparison.visibility_delta:.4f}."
    )

    return Evidence(
        evidence_id=evidence_id,
        source_group=source_group,
        signal="face.visibility_comparison",
        status=status,
        kind=EvidenceKind.FACT,
        summary=summary,
        details={
            "comparison_status": comparison.status.value,
            "visibility_delta": comparison.visibility_delta,
            "eye_visibility_consistent": comparison.eye_visibility_consistent,
            "lower_face_consistent": comparison.lower_face_consistent,
            "covering_consistent": comparison.covering_consistent,
            "identity_status": comparison.identity_status,
            "limitations": list(comparison.limitations),
        },
    )
