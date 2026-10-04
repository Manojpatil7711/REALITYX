from realityx.c2pa import (
    ContentCredential,
    CredentialStatus,
    credential_digest,
    validate_content_credential,
)


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
