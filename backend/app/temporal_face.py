from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TemporalConsistency(StrEnum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class TemporalObservation:
    frame_index: int
    face_visible_fraction: float
    eye_region_visible: bool
    lower_face_visible: bool
    covering_detected: bool | None


@dataclass(frozen=True)
class TemporalFaceAssessment:
    frames_analyzed: int
    visibility_consistency: TemporalConsistency
    covering_consistency: TemporalConsistency
    stable_observations: int
    identity_status: str = "UNVERIFIED"


def assess_temporal_face_consistency(
    observations: list[TemporalObservation],
) -> TemporalFaceAssessment:
    if not observations:
        return TemporalFaceAssessment(
            frames_analyzed=0,
            visibility_consistency=TemporalConsistency.INSUFFICIENT,
            covering_consistency=TemporalConsistency.INSUFFICIENT,
            stable_observations=0,
        )

    visible = [o.face_visible_fraction for o in observations]
    covering = [o.covering_detected for o in observations if o.covering_detected is not None]

    # A conservative temporal signal: observations must agree reasonably on
    # visibility state; a single anomalous frame never establishes manipulation.
    visible_states = {
        "clear" if value >= 0.80 else
        "partial" if value >= 0.25 else
        "occluded" if value > 0.0 else
        "not_visible"
        for value in visible
    }
    visibility_consistency = (
        TemporalConsistency.CONSISTENT
        if len(visible_states) <= 1
        else TemporalConsistency.INCONSISTENT
        if len(observations) >= 3
        else TemporalConsistency.INSUFFICIENT
    )

    covering_states = set(covering)
    covering_consistency = (
        TemporalConsistency.INSUFFICIENT
        if not covering
        else TemporalConsistency.CONSISTENT
        if len(covering_states) == 1
        else TemporalConsistency.INCONSISTENT
        if len(covering) >= 3
        else TemporalConsistency.INSUFFICIENT
    )

    stable = sum(
        1 for observation in observations
        if observation.eye_region_visible or observation.lower_face_visible
    )

    return TemporalFaceAssessment(
        frames_analyzed=len(observations),
        visibility_consistency=visibility_consistency,
        covering_consistency=covering_consistency,
        stable_observations=stable,
    )
