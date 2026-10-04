import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from realityx.c2pa import (
    ContentCredential,
    CredentialStatus,
    credential_digest,
    credential_signing_payload,
    credential_to_evidence,
    validate_content_credential,
    verify_credential_signature,
)
from realityx.contracts import EvidenceKind, SignalStatus


ARTIFACT = "a" * 64


def credential(**overrides):
    data = {
        "manifest_id": "urn:realityx:manifest:1",
        "artifact_sha256": ARTIFACT,
        "issuer": "example",
        "claim": "Captured by a documented camera workflow",
        "signature_algorithm": "Ed25519",
        "signature": "signed-payload",
    }
    data.update(overrides)
    return ContentCredential(**data)


def signed_credential(private_key):
    unsigned = credential()
    signature = private_key.sign(credential_signing_payload(unsigned))
    return unsigned.model_copy(
        update={"signature": base64.b64encode(signature).decode("ascii")}
    )


def test_artifact_binding_fails_closed():
    assert validate_content_credential(
        credential(artifact_sha256="b" * 64), artifact_sha256=ARTIFACT
    ) == CredentialStatus.INVALID


def test_untrusted_but_valid_credential_stays_provenance_only():
    assert validate_content_credential(
        credential(), artifact_sha256=ARTIFACT, trusted_issuer=False
    ) == CredentialStatus.VALID


def test_trusted_issuer_is_explicit():
    assert validate_content_credential(
        credential(), artifact_sha256=ARTIFACT, trusted_issuer=True
    ) == CredentialStatus.TRUSTED


def test_conflict_overrides_trust():
    assert validate_content_credential(
        credential(), artifact_sha256=ARTIFACT, trusted_issuer=True, conflicting=True
    ) == CredentialStatus.CONFLICTING


def test_missing_credential_is_explicit():
    assert validate_content_credential(None, artifact_sha256=ARTIFACT) == CredentialStatus.ABSENT


def test_credential_digest_is_deterministic_and_claim_bound():
    first = credential_digest(credential())
    second = credential_digest(credential())
    changed = credential_digest(credential(claim="Different claim"))
    assert first == second
    assert first != changed


def test_ed25519_signature_verifies():
    private_key = Ed25519PrivateKey.generate()
    signed = signed_credential(private_key)
    public_key = base64.b64encode(private_key.public_key().public_bytes_raw()).decode("ascii")
    assert verify_credential_signature(signed, public_key_b64=public_key) is True


def test_tampered_claim_fails_signature():
    private_key = Ed25519PrivateKey.generate()
    signed = signed_credential(private_key)
    tampered = signed.model_copy(update={"claim": "Tampered"})
    public_key = base64.b64encode(private_key.public_key().public_bytes_raw()).decode("ascii")
    assert verify_credential_signature(tampered, public_key_b64=public_key) is False


def test_invalid_ed25519_signature_fails_closed():
    private_key = Ed25519PrivateKey.generate()
    signed = signed_credential(private_key)
    invalid = signed.model_copy(update={"signature": "not-a-valid-signature"})
    public_key = base64.b64encode(private_key.public_key().public_bytes_raw()).decode("ascii")
    assert verify_credential_signature(invalid, public_key_b64=public_key) is False


def test_unsupported_algorithm_fails_closed():
    private_key = Ed25519PrivateKey.generate()
    signed = signed_credential(private_key)
    unsupported = signed.model_copy(update={"signature_algorithm": "rsa"})
    public_key = base64.b64encode(private_key.public_key().public_bytes_raw()).decode("ascii")
    assert verify_credential_signature(unsupported, public_key_b64=public_key) is False


def test_c2pa_maps_to_fact_not_verdict():
    evidence = credential_to_evidence(
        credential(), artifact_sha256=ARTIFACT, status=CredentialStatus.TRUSTED,
        signature_valid=True,
    )
    assert evidence.kind is EvidenceKind.FACT
    assert evidence.verdict is None
    assert evidence.status is SignalStatus.AVAILABLE


def test_invalid_c2pa_is_failed_evidence():
    evidence = credential_to_evidence(
        credential(artifact_sha256="b" * 64), artifact_sha256=ARTIFACT,
        status=CredentialStatus.INVALID,
    )
    assert evidence.kind is EvidenceKind.FACT
    assert evidence.verdict is None
    assert evidence.status is SignalStatus.FAILED
