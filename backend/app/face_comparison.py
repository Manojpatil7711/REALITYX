from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FaceComparisonStatus(StrEnum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class FaceVisibilityComparison:
    status: FaceComparisonStatus
    visibility_delta: float
    eye_visibility_consistent: bool
    lower_face_consistent: bool
    covering_consistent: bool | None
    identity_status: str = "UNVERIFIED"
    limitations: tuple[str, ...] = ()


def compare_face_visibility(
    *,
    first_visible_fraction: float,
    second_visible_fraction: float,
    first_eye_region_visible: bool,
    second_eye_region_visible: bool,
    first_lower_face_visible: bool,
    second_lower_face_visible: bool,
    first_covering_detected: bool | None = None,
    second_covering_detected: bool | None = None,
    minimum_observable_fraction: float = 0.10,
) -> FaceVisibilityComparison:
    for value, name in (
        (first_visible_fraction, "first_visible_fraction"),
        (second_visible_fraction, "second_visible_fraction"),
    ):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1")
    if not 0.0 <= minimum_observable_fraction <= 1.0:
        raise ValueError("minimum_observable_fraction must be between 0 and 1")

    first_observable = first_visible_fraction >= minimum_observable_fraction
    second_observable = second_visible_fraction >= minimum_observable_fraction
    delta = round(abs(first_visible_fraction - second_visible_fraction), 4)

    if not first_observable or not second_observable:
        return FaceVisibilityComparison(
            status=FaceComparisonStatus.INSUFFICIENT,
            visibility_delta=delta,
            eye_visibility_consistent=first_eye_region_visible == second_eye_region_visible,
            lower_face_consistent=first_lower_face_visible == second_lower_face_visible,
            covering_consistent=(
                None
                if first_covering_detected is None or second_covering_detected is None
                else first_covering_detected == second_covering_detected
            ),
            limitations=(
                "One or both images contain insufficient observable face evidence.",
                "This comparison does not establish that the depicted person is the same individual.",
            ),
        )

    eye_consistent = first_eye_region_visible == second_eye_region_visible
    lower_consistent = first_lower_face_visible == second_lower_face_visible
    covering_consistent = (
        None
        if first_covering_detected is None or second_covering_detected is None
        else first_covering_detected == second_covering_detected
    )

    hard_conflict = (
        delta >= 0.75
        or (covering_consistent is False and delta >= 0.45)
    )

    if hard_conflict:
        status = FaceComparisonStatus.INCONSISTENT
    elif delta <= 0.35 and eye_consistent and lower_consistent:
        status = FaceComparisonStatus.CONSISTENT
    else:
        status = FaceComparisonStatus.INSUFFICIENT

    return FaceVisibilityComparison(
        status=status,
        visibility_delta=delta,
        eye_visibility_consistent=eye_consistent,
        lower_face_consistent=lower_consistent,
        covering_consistent=covering_consistent,
        limitations=(
            "Visibility consistency is not identity verification.",
            "Different camera angle, pose, lighting, compression, or occlusion can change observable face regions.",
        ),
    )
