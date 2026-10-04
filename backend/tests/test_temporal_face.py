from app.temporal_face import (
    TemporalConsistency,
    TemporalObservation,
    assess_temporal_face_consistency,
)


def test_empty_sequence_is_insufficient():
    result = assess_temporal_face_consistency([])
    assert result.frames_analyzed == 0
    assert result.visibility_consistency is TemporalConsistency.INSUFFICIENT


def test_stable_masked_face_is_temporally_consistent():
    observations = [
        TemporalObservation(i, 0.42, True, False, True)
        for i in range(8)
    ]
    result = assess_temporal_face_consistency(observations)
    assert result.frames_analyzed == 8
    assert result.visibility_consistency is TemporalConsistency.CONSISTENT
    assert result.covering_consistency is TemporalConsistency.CONSISTENT
    assert result.identity_status == "UNVERIFIED"


def test_mixed_visibility_is_not_silently_normalized():
    observations = [
        TemporalObservation(0, 0.10, False, False, True),
        TemporalObservation(1, 0.90, True, True, False),
        TemporalObservation(2, 0.45, True, False, True),
    ]
    result = assess_temporal_face_consistency(observations)
    assert result.visibility_consistency is TemporalConsistency.INCONSISTENT
    assert result.covering_consistency is TemporalConsistency.INCONSISTENT
