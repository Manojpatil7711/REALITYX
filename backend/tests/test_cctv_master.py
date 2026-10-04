from backend.app.cctv_master import CCTVVerificationStatus, assess_cctv_face_evidence
from backend.app.face_visibility import assess_face_visibility
from backend.app.temporal_face import (
    TemporalObservation,
    assess_temporal_face_consistency,
)


def test_cctv_master_supports_visible_face_without_identity_claim():
    face = assess_face_visibility(
        visible_fraction=0.62,
        eye_region_visible=True,
        lower_face_visible=False,
        covering_detected=True,
        frame_count=8,
    )
    temporal = assess_temporal_face_consistency(
        [
            TemporalObservation(i, 0.62, True, False, True)
            for i in range(8)
        ]
    )

    result = assess_cctv_face_evidence(face=face, temporal=temporal)

    assert result.status == CCTVVerificationStatus.SUPPORTED
    assert result.identity_status == "UNVERIFIED"
    assert result.reconstruction_allowed is False


def test_cctv_master_abstains_when_visibility_is_inconsistent():
    face = assess_face_visibility(
        visible_fraction=0.45,
        eye_region_visible=True,
        lower_face_visible=False,
        frame_count=3,
    )
    temporal = assess_temporal_face_consistency(
        [
            TemporalObservation(0, 0.9, True, True, False),
            TemporalObservation(1, 0.05, False, False, None),
            TemporalObservation(2, 0.45, True, False, True),
        ]
    )

    result = assess_cctv_face_evidence(face=face, temporal=temporal)

    assert result.status == CCTVVerificationStatus.CONFLICTING


def test_cctv_master_does_not_infer_mask_from_missing_face():
    face = assess_face_visibility(
        visible_fraction=0.0,
        eye_region_visible=False,
        lower_face_visible=False,
        frame_count=1,
    )
    temporal = assess_temporal_face_consistency(
        [TemporalObservation(0, 0.0, False, False, None)]
    )

    result = assess_cctv_face_evidence(face=face, temporal=temporal)

    assert result.status == CCTVVerificationStatus.INSUFFICIENT
    assert "absence of a face is not evidence of a mask" in " ".join(result.limitations)
