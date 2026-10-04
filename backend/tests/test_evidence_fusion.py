from app.contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict, VerificationResult
from app.evidence_fusion import fuse_evidence
from app.evidence_graph import EvidenceGraph


def signal(verdict=None, confidence=0.9, status=SignalStatus.AVAILABLE, name="test", source_group=None, parents=None):
    return Evidence(
        evidence_id=f"{name}-{source_group or name}",
        source_group=source_group or name,
        parent_evidence_ids=parents or [],
        signal=name,
        status=status,
        summary="test",
        kind=EvidenceKind.VERDICT if verdict is not None else EvidenceKind.FACT,
        verdict=SignalVerdict(verdict) if verdict is not None else None,
        confidence=confidence,
    )


def test_empty_evidence_abstains():
    decision = fuse_evidence([])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence == 0.0


def test_failed_signal_is_not_negative_evidence():
    decision = fuse_evidence([signal("authentic", 0.9), signal(status=SignalStatus.FAILED)])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence < 0.70


def test_weak_evidence_abstains():
    assert fuse_evidence([signal("authentic", 0.69)]).result is VerificationResult.UNCERTAIN


def test_conflicting_evidence_abstains_and_is_capped():
    decision = fuse_evidence([signal("authentic", 0.95, source_group="source-a"), signal("manipulated", 0.94, source_group="source-b")])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.conflict is True
    assert decision.confidence <= 0.49


def test_consistent_negative_evidence_can_be_inauthentic():
    decision = fuse_evidence([
        signal("manipulated", 0.95, name="m1", source_group="a"),
        signal("ai_generated", 0.92, name="m2", source_group="b"),
        signal("inauthentic", 0.90, name="m3", source_group="c"),
    ])
    assert decision.result is VerificationResult.INAUTHENTIC
    assert decision.confidence >= 0.70


def test_missing_verdict_does_not_create_a_public_verdict():
    decision = fuse_evidence([signal(None, 0.99)])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence == 0.0


def test_factual_signals_do_not_inflate_verdict_coverage():
    verdict_only = fuse_evidence([signal("authentic", 0.9, name="model")])
    with_facts = fuse_evidence([
        signal("authentic", 0.9, name="model"),
        signal(None, 1.0, name="integrity"),
        signal(None, 1.0, name="image_structure"),
        signal(None, 1.0, name="metadata"),
    ])
    assert with_facts.result is verdict_only.result
    assert with_facts.confidence == verdict_only.confidence


def test_ten_correlated_signals_count_as_one_independent_source():
    signals = [signal("authentic", 0.95, name=f"model-{i}", source_group="same-origin") for i in range(10)]
    one = fuse_evidence([signals[0]])
    many = fuse_evidence(signals)
    assert many.independent_source_count == 1
    assert many.confidence == one.confidence


def test_two_independent_sources_count_as_two():
    decision = fuse_evidence([
        signal("authentic", 0.9, name="a", source_group="source-a"),
        signal("authentic", 0.9, name="b", source_group="source-b"),
    ])
    assert decision.independent_source_count == 2
    assert decision.confidence > fuse_evidence([signal("authentic", 0.9)]).confidence


def test_shared_parent_lineage_is_recorded_and_digest_is_deterministic():
    root = signal("authentic", 0.9, name="root", source_group="origin")
    child = signal("authentic", 0.9, name="child", source_group="derived", parents=[root.evidence_id])
    graph_a = EvidenceGraph.from_evidence([root, child])
    graph_b = EvidenceGraph.from_evidence([child, root])
    assert root.evidence_id in child.parent_evidence_ids
    assert graph_a.digest() == graph_b.digest()


def test_malformed_provenance_abstains_instead_of_crashing():
    decision = fuse_evidence([
        signal("authentic", 0.95, name="model", source_group="model", parents=["missing-parent"]),
    ])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence == 0.0
    assert decision.independent_source_count == 0
    assert decision.conflict is False


def test_boundary_confidence_below_threshold_abstains():
    decision = fuse_evidence([signal("authentic", 0.70, name="boundary")])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence < 0.70


def test_three_independent_high_confidence_sources_reach_full_coverage():
    decision = fuse_evidence([
        signal("authentic", 0.90, name="a", source_group="a"),
        signal("authentic", 0.90, name="b", source_group="b"),
        signal("authentic", 0.90, name="c", source_group="c"),
    ])
    assert decision.independent_source_count == 3
    assert decision.result is VerificationResult.VERIFIED
    assert decision.confidence == 0.90


def test_malformed_cycle_abstains_closed():
    first = signal("authentic", 0.95, name="a", source_group="a", parents=["b"])
    second = signal("authentic", 0.95, name="b", source_group="b", parents=[first.evidence_id])
    decision = fuse_evidence([first, second])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence == 0.0
    assert decision.independent_source_count == 0
