import base64
import os

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.signed_verification_proof import sign_verification_proof, validate_signed_proof
from app.verification_policy import AuthorityStatus, UnifiedVerificationDecision
from app.contracts import VerificationResult
from app.risk_assessment import RecommendedAction, RiskAssessment, RiskDomain, RiskLevel
from app.verification_proof import build_verification_proof

def proof():
    risk = RiskAssessment(RiskDomain.UNKNOWN, RiskLevel.UNCERTAIN, 0.0,
                          RecommendedAction.REVERIFY, ("test",), 0)
    decision = UnifiedVerificationDecision(
        VerificationResult.UNCERTAIN, 0.42, risk, "abc123", 1, False,
        "2050.1", AuthorityStatus.UNAVAILABLE)
    return build_verification_proof(decision)

def test_signed_proof_round_trip(monkeypatch):
    private = Ed25519PrivateKey.generate()
    raw = private.private_bytes_raw()
    public = private.public_key().public_bytes_raw()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "key-test")
    monkeypatch.setenv("REALITYX_SIGNING_PRIVATE_KEY_B64", base64.b64encode(raw).decode())
    monkeypatch.setenv("REALITYX_SIGNING_PUBLIC_KEY_B64", base64.b64encode(public).decode())
    signed = sign_verification_proof(proof())
    assert signed.signature_algorithm == "Ed25519:key-test"
    assert validate_signed_proof(signed)

def test_tampered_signature_fails(monkeypatch):
    private = Ed25519PrivateKey.generate()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "key-test")
    monkeypatch.setenv("REALITYX_SIGNING_PRIVATE_KEY_B64",
                       base64.b64encode(private.private_bytes_raw()).decode())
    monkeypatch.setenv("REALITYX_SIGNING_PUBLIC_KEY_B64",
                       base64.b64encode(private.public_key().public_bytes_raw()).decode())
    signed = sign_verification_proof(proof())
    tampered = signed.__class__(signed.proof, signed.signature_algorithm, base64.b64encode(b"bad").decode())
    assert not validate_signed_proof(tampered)

def test_missing_signing_credentials_fail(monkeypatch):
    monkeypatch.delenv("REALITYX_SIGNING_KEY_ID", raising=False)
    monkeypatch.delenv("REALITYX_SIGNING_PRIVATE_KEY_B64", raising=False)
    try:
        sign_verification_proof(proof())
    except RuntimeError:
        return
    assert False
