from pytest import raises

from app.contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict
from app.evidence_graph import analyze_evidence_graph


def ev(id, group, signal, *, parents=None, verdict=None):
    return Evidence(
        evidence_id=id,
        source_group=group,
        signal=signal,
        status=SignalStatus.AVAILABLE,
        kind=EvidenceKind.FACT,
        summary=signal,
        parent_evidence_ids=parents or [],
        verdict=verdict,
        confidence=0.9,
    )


def test_derived_evidence_does_not_create_new_independent_source():
    result = analyze_evidence_graph([
        ev("img", "image-engine", "manipulation_detected"),
        ev("derived", "fusion-engine", "risk", parents=["img"]),
    ])
    assert result.independent_sources == 1


def test_independent_modalities_are_counted_separately():
    result = analyze_evidence_graph([
        ev("img", "image-engine", "manipulation_detected"),
        ev("audio", "audio-engine", "ai_generated"),
    ])
    assert result.independent_sources == 2


def test_conflicting_verdicts_are_preserved():
    result = analyze_evidence_graph([
        ev("a", "engine-a", "authenticity", verdict=SignalVerdict.AUTHENTIC),
        ev("b", "engine-b", "authenticity", verdict=SignalVerdict.MANIPULATED),
    ])
    assert result.contradictions == (
        ("authenticity", "authentic vs manipulated"),
    )


def test_missing_parent_is_rejected():
    with raises(ValueError, match="unknown parent"):
        analyze_evidence_graph([
            ev("child", "fusion", "risk", parents=["missing"]),
        ])


def test_cycle_is_rejected():
    with raises(ValueError, match="cycle"):
        analyze_evidence_graph([
            ev("a", "a", "x", parents=["b"]),
            ev("b", "b", "y", parents=["a"]),
        ])
