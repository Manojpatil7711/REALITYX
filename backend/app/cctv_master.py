from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .face_visibility import FaceVisibilityAssessment
from .temporal_face import TemporalFaceAssessment


class CCTVVerificationStatus(StrEnum):
    SUPPORTED = "supported"
    INSUFFICIENT = "insufficient"
    CONFLICTING = "conflicting"


class IdentityStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class CCTVMasterAssessment:
    status: CCTVVerificationStatus
    face_visibility: str
    visible_fraction: float
    covering: str
    temporal_consistency: str
    evidence_strength: str
    identity_status: str
    reconstruction_allowed: bool
    limitations: tuple[str, ...]


def assess_cctv_face_evidence(
    *,
    face: FaceVisibilityAssessment,
    temporal: TemporalFaceAssessment,
) -> CCTVMasterAssessment:
    limitations: list[str] = [
        "Face visibility evidence does not establish a person's identity.",
        "A reconstructed or AI-generated face must not be treated as identity evidence.",
    ]

    if temporal.frames_analyzed == 0:
        status = CCTVVerificationStatus.INSUFFICIENT
    elif temporal.visibility_consistency.value == "inconsistent":
        status = CCTVVerificationStatus.CONFLICTING
        limitations.append("Face visibility changes across analyzed frames; treat the observation conservatively.")
    elif face.visibility.value == "not_visible":
        status = CCTVVerificationStatus.INSUFFICIENT
        limitations.append("No observable face region was established; absence of a face is not evidence of a mask.")
    else:
        status = CCTVVerificationStatus.SUPPORTED

    return CCTVMasterAssessment(
        status=status,
        face_visibility=face.visibility.value,
        visible_fraction=face.visible_fraction,
        covering=face.covering.value,
        temporal_consistency=temporal.visibility_consistency.value,
        evidence_strength=face.evidence_strength,
        identity_status=IdentityStatus.UNVERIFIED.value,
        reconstruction_allowed=False,
        limitations=tuple(limitations),
    )
