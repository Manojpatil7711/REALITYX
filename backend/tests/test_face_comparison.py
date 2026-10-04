from backend.app.face_comparison import FaceComparisonStatus, compare_face_visibility


def test_comparison_is_consistent_without_identity_claim():
    result = compare_face_visibility(
        first_visible_fraction=0.60,
        second_visible_fraction=0.72,
        first_eye_region_visible=True,
        second_eye_region_visible=True,
        first_lower_face_visible=False,
        second_lower_face_visible=False,
        first_covering_detected=True,
        second_covering_detected=True,
    )

    assert result.status == FaceComparisonStatus.CONSISTENT
    assert result.identity_status == "UNVERIFIED"


def test_comparison_abstains_when_one_face_is_not_observable():
    result = compare_face_visibility(
        first_visible_fraction=0.0,
        second_visible_fraction=0.70,
        first_eye_region_visible=False,
        second_eye_region_visible=True,
        first_lower_face_visible=False,
        second_lower_face_visible=True,
    )

    assert result.status == FaceComparisonStatus.INSUFFICIENT


def test_comparison_detects_large_visibility_conflict():
    result = compare_face_visibility(
        first_visible_fraction=0.95,
        second_visible_fraction=0.10,
        first_eye_region_visible=True,
        second_eye_region_visible=False,
        first_lower_face_visible=True,
        second_lower_face_visible=False,
        first_covering_detected=False,
        second_covering_detected=True,
    )

    assert result.status == FaceComparisonStatus.INCONSISTENT


def test_invalid_fraction_rejected():
    try:
        compare_face_visibility(
            first_visible_fraction=1.1,
            second_visible_fraction=0.5,
            first_eye_region_visible=True,
            second_eye_region_visible=True,
            first_lower_face_visible=True,
            second_lower_face_visible=True,
        )
    except ValueError:
        return
    raise AssertionError("invalid visibility fraction must fail")
