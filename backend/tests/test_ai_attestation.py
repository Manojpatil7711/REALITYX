from app.contracts import Evidence, EvidenceKind, SignalStatus
from app.ai_attestation import (
    AIProvider, ProviderTrust, attest_evidence, evidence_digest,
    validate_attestation,
)

def ev():
    return Evidence(evidence_id="e1", source_group="provider-a",
                    signal="integrity", status=SignalStatus.AVAILABLE,
                    kind=EvidenceKind.FACT, summary="ok", confidence=0.9)

def test_attestation_is_deterministic():
    provider = AIProvider("provider-a", "1.2.0", ProviderTrust.REGISTERED)
    a = attest_evidence(provider, ev())
    assert a.evidence_digest == evidence_digest(ev())
    assert validate_attestation(a)

def test_tampered_evidence_fails_validation():
    provider = AIProvider("provider-a", "1.2.0", ProviderTrust.REGISTERED)
    a = attest_evidence(provider, ev())
    changed = a.evidence.model_copy(update={"summary": "changed"})
    tampered = a.__class__(provider=a.provider, evidence=changed,
                           evidence_digest=a.evidence_digest)
    assert not validate_attestation(tampered)

def test_revoked_provider_cannot_attest():
    provider = AIProvider("provider-a", "1.2.0", ProviderTrust.REVOKED)
    try:
        attest_evidence(provider, ev())
    except ValueError:
        return
    assert False, "revoked provider was accepted"

def test_attestation_does_not_grant_trust_automatically():
    provider = AIProvider("provider-a", "1.2.0", ProviderTrust.UNTRUSTED)
    a = attest_evidence(provider, ev())
    assert validate_attestation(a)
    assert a.provider.trust is ProviderTrust.UNTRUSTED
