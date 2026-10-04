import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.ai_attestation import AIProvider, ProviderTrust
from app.signed_verification_proof import (
    SignedProofTrust,
    sign_verification_proof,
    verify_signed_proof,
)
from app.trust_registry import KeyStatus, TrustRecord, TrustRegistry, register_key
from app.verification_policy import AuthorityStatus, UnifiedVerificationDecision
from app.contracts import VerificationResult
from app.risk_assessment import RecommendedAction, RiskAssessment, RiskDomain, RiskLevel
from app.verification_proof import build_verification_proof


def _proof():
    risk = RiskAssessment(
        RiskDomain.UNKNOWN, RiskLevel.UNCERTAIN, 0.0,
        RecommendedAction.REVERIFY, ("test",), 0,
    )
    decision = UnifiedVerificationDecision(
        VerificationResult.UNCERTAIN, 0.42, risk, "abc123", 1, False,
        "2050.1", AuthorityStatus.UNAVAILABLE,
    )
    return build_verification_proof(decision)


def _signed(monkeypatch):
    private = Ed25519PrivateKey.generate()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "registry-key")
    monkeypatch.setenv(
        "REALITYX_SIGNING_PRIVATE_KEY_B64",
        base64.b64encode(private.private_bytes_raw()).decode(),
    )
    return private, sign_verification_proof(_proof())


def _registry(private, *, expires_at=None):
    public = base64.b64encode(private.public_key().public_bytes_raw()).decode()
    registry = TrustRegistry()
    registry.register(
        register_key(
            AIProvider("provider-a", "2.0", ProviderTrust.ATTESTED),
            "registry-key",
            public,
            expires_at=expires_at,
        )
    )
    return registry


def test_registry_backed_verification_is_independent_of_public_key_environment(monkeypatch):
    private, signed = _signed(monkeypatch)
    monkeypatch.delenv("REALITYX_SIGNING_PUBLIC_KEY_B64", raising=False)
    result = verify_signed_proof(signed, _registry(private))
    assert result.cryptographically_valid
    assert result.trusted_now
    assert result.trust_status is SignedProofTrust.ACTIVE
    assert result.key_id == "registry-key"


def test_unknown_key_fails_closed(monkeypatch):
    _, signed = _signed(monkeypatch)
    result = verify_signed_proof(signed, TrustRegistry())
    assert not result.cryptographically_valid
    assert not result.trusted_now
    assert result.trust_status is SignedProofTrust.UNKNOWN


def test_revoked_key_keeps_historical_crypto_validity(monkeypatch):
    private, signed = _signed(monkeypatch)
    registry = _registry(private)
    record = registry.get("registry-key")
    revoked = record.key.__class__(
        record.key.provider_id, record.key.key_id,
        record.key.public_key_fingerprint, KeyStatus.REVOKED,
        record.key.created_at, record.key.expires_at,
        record.key.rotated_at, record.key.revoked_at, record.key.public_key,
    )
    registry.register(TrustRecord(record.provider, revoked, record.registry_version))
    result = verify_signed_proof(signed, registry)
    assert result.cryptographically_valid
    assert not result.trusted_now
    assert result.trust_status is SignedProofTrust.REVOKED


def test_rotated_key_keeps_historical_crypto_validity(monkeypatch):
    private, signed = _signed(monkeypatch)
    registry = _registry(private)
    record = registry.get("registry-key")
    rotated = record.key.__class__(
        record.key.provider_id, record.key.key_id,
        record.key.public_key_fingerprint, KeyStatus.ROTATED,
        record.key.created_at, record.key.expires_at,
        record.key.rotated_at, record.key.revoked_at, record.key.public_key,
    )
    registry.register(TrustRecord(record.provider, rotated, record.registry_version))
    result = verify_signed_proof(signed, registry)
    assert result.cryptographically_valid
    assert not result.trusted_now
    assert result.trust_status is SignedProofTrust.ROTATED


def test_expired_key_keeps_historical_crypto_validity(monkeypatch):
    private, signed = _signed(monkeypatch)
    result = verify_signed_proof(
        signed, _registry(private, expires_at="2026-01-01T00:00:00Z")
    )
    assert result.cryptographically_valid
    assert not result.trusted_now
    assert result.trust_status is SignedProofTrust.EXPIRED


def test_tampered_signature_is_not_cryptographically_valid(monkeypatch):
    private, signed = _signed(monkeypatch)
    tampered = signed.__class__(
        signed.proof, signed.signature_algorithm,
        base64.b64encode(b"bad").decode(),
    )
    result = verify_signed_proof(tampered, _registry(private))
    assert not result.cryptographically_valid
    assert not result.trusted_now
