from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FaceVisibility(StrEnum):
    CLEAR = "clear"
    PARTIAL = "partial"
    OCCLUDED = "occluded"
    NOT_VISIBLE = "not_visible"
    UNCERTAIN = "uncertain"


class CoveringStatus(StrEnum):
    PRESENT = "present"
    NOT_DETECTED = "not_detected"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class FaceVisibilityAssessment:
    visibility: FaceVisibility
    covering: CoveringStatus
    visible_fraction: float
    evidence_strength: str
    identity_status: str = "UNVERIFIED"
    reconstruction_allowed: bool = False


def assess_face_visibility(
    *,
    visible_fraction: float,
    eye_region_visible: bool,
    lower_face_visible: bool,
    covering_detected: bool | None = None,
    frame_count: int = 1,
) -> FaceVisibilityAssessment:
    """Conservative face-visibility assessment for video/CCTV evidence.

    This function does not identify a person and never reconstructs an unseen
    face. It converts detector observations into an auditable evidence state.
    """
    if not 0.0 <= visible_fraction <= 1.0:
        raise ValueError("visible_fraction must be between 0 and 1")
    if frame_count < 1:
        raise ValueError("frame_count must be positive")

    if visible_fraction >= 0.80 and lower_face_visible:
        visibility = FaceVisibility.CLEAR
    elif visible_fraction >= 0.25 and eye_region_visible:
        visibility = FaceVisibility.PARTIAL
    elif visible_fraction > 0.0:
        visibility = FaceVisibility.OCCLUDED
    else:
        visibility = FaceVisibility.NOT_VISIBLE

    if covering_detected is True:
        covering = CoveringStatus.PRESENT
    elif covering_detected is False:
        covering = CoveringStatus.NOT_DETECTED
    else:
        covering = CoveringStatus.UNCERTAIN

    if frame_count >= 8 and visibility in {
        FaceVisibility.CLEAR,
        FaceVisibility.PARTIAL,
        FaceVisibility.OCCLUDED,
    }:
        strength = "STRONG"
    elif frame_count >= 3:
        strength = "MEDIUM"
    else:
        strength = "WEAK"

    return FaceVisibilityAssessment(
        visibility=visibility,
        covering=covering,
        visible_fraction=round(visible_fraction, 4),
        evidence_strength=strength,
    )
