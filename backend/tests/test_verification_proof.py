from app.contracts import VerificationResult
from app.risk_assessment import RecommendedAction, RiskAssessment, RiskDomain, RiskLevel
from app.verification_policy import AuthorityStatus, UnifiedVerificationDecision
from app.verification_proof import build_verification_proof, validate_verification_proof

def decision():
    risk = RiskAssessment(
        RiskDomain.UNKNOWN,
        RiskLevel.UNCERTAIN,
        0.0,
        RecommendedAction.REVERIFY,
        ("test decision",),
        0,
    )
    return UnifiedVerificationDecision(
        result=VerificationResult.UNCERTAIN,
        confidence=0.42,
        risk=risk,
        evidence_graph_digest="abc123",
        independent_source_count=1,
        conflict=False,
        policy_version="2050.1",
        authority_status=AuthorityStatus.UNAVAILABLE,
    )

def test_proof_is_deterministic_and_valid():
    a = build_verification_proof(decision())
    b = build_verification_proof(decision())
    assert a.proof_digest == b.proof_digest
    assert validate_verification_proof(a)

def test_tampered_proof_fails():
    proof = build_verification_proof(decision())
    tampered = proof.__class__(**{**proof.__dict__, "confidence": 0.99})
    assert not validate_verification_proof(tampered)

def test_proof_does_not_change_decision():
    proof = build_verification_proof(decision())
    assert proof.result == "uncertain"
    assert proof.confidence == 0.42
