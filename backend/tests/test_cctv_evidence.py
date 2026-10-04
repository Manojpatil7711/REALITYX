from backend.app.cctv_evidence import cctv_master_to_evidence, face_comparison_to_evidence
from backend.app.cctv_master import assess_cctv_face_evidence
from backend.app.face_comparison import compare_face_visibility
from backend.app.face_visibility import assess_face_visibility
from backend.app.temporal_face import TemporalObservation, assess_temporal_face_consistency
from backend.app.contracts import SignalStatus


def test_cctv_master_maps_to_fact_evidence():
    face = assess_face_visibility(
        visible_fraction=0.62,
        eye_region_visible=True,
        lower_face_visible=False,
        covering_detected=True,
        frame_count=8,
    )
    temporal = assess_temporal_face_consistency(
        [TemporalObservation(i, 0.62, True, False, True) for i in range(8)]
    )
    assessment = assess_cctv_face_evidence(face=face, temporal=temporal)
    evidence = cctv_master_to_evidence(assessment, evidence_id="cctv-1")

    assert evidence.signal == "cctv.face_visibility"
    assert evidence.status == SignalStatus.AVAILABLE
    assert evidence.kind.value == "fact"
    assert evidence.details["identity_status"] == "UNVERIFIED"


def test_face_comparison_maps_insufficient_to_unavailable():
    comparison = compare_face_visibility(
        first_visible_fraction=0.0,
        second_visible_fraction=0.7,
        first_eye_region_visible=False,
        second_eye_region_visible=True,
        first_lower_face_visible=False,
        second_lower_face_visible=True,
    )
    evidence = face_comparison_to_evidence(comparison, evidence_id="compare-1")

    assert evidence.status == SignalStatus.UNAVAILABLE
    assert evidence.details["identity_status"] == "UNVERIFIED"
