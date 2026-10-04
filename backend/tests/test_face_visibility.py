from app.face_visibility import (
    CoveringStatus,
    FaceVisibility,
    assess_face_visibility,
)


def test_clear_face_requires_lower_face_visibility():
    result = assess_face_visibility(
        visible_fraction=0.9,
        eye_region_visible=True,
        lower_face_visible=True,
        frame_count=10,
    )
    assert result.visibility is FaceVisibility.CLEAR
    assert result.evidence_strength == "STRONG"
    assert result.identity_status == "UNVERIFIED"
    assert result.reconstruction_allowed is False


def test_eyes_visible_is_partial_not_identity():
    result = assess_face_visibility(
        visible_fraction=0.45,
        eye_region_visible=True,
        lower_face_visible=False,
        covering_detected=True,
        frame_count=8,
    )
    assert result.visibility is FaceVisibility.PARTIAL
    assert result.covering is CoveringStatus.PRESENT
    assert result.identity_status == "UNVERIFIED"


def test_no_face_is_not_called_a_mask():
    result = assess_face_visibility(
        visible_fraction=0.0,
        eye_region_visible=False,
        lower_face_visible=False,
        covering_detected=None,
    )
    assert result.visibility is FaceVisibility.NOT_VISIBLE
    assert result.covering is CoveringStatus.UNCERTAIN


def test_invalid_inputs_fail_closed():
    try:
        assess_face_visibility(
            visible_fraction=1.1,
            eye_region_visible=True,
            lower_face_visible=True,
        )
    except ValueError as exc:
        assert "visible_fraction" in str(exc)
    else:
        raise AssertionError("invalid visibility should be rejected")
