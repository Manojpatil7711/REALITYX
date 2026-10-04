"""Provider-neutral Content Credentials / C2PA trust boundary.

Credentials are provenance evidence. A valid credential never becomes an
authenticity verdict by itself; artifact binding, signature validity, and
issuer trust remain explicit.
"""

from __future__ import annotations

import base64
from enum import StrEnum
from hashlib import sha256

from cryptography.exceptions import InvalidSignature
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .attestation import canonical_json
from .contracts import Evidence, EvidenceKind, SignalStatus


class CredentialStatus(StrEnum):
    ABSENT = "absent"
    INVALID = "invalid"
    UNTRUSTED = "untrusted"
    VALID = "valid"
    TRUSTED = "trusted"
    CONFLICTING = "conflicting"


class ContentCredential(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest_id: str = Field(min_length=1, max_length=512)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    issuer: str = Field(min_length=1, max_length=256)
    claim: str = Field(min_length=1, max_length=2000)
    signature_algorithm: str = Field(min_length=1, max_length=64)
    signature: str = Field(min_length=1, max_length=8192)

    @model_validator(mode="after")
    def normalize_algorithm(self) -> "ContentCredential":
        self.signature_algorithm = self.signature_algorithm.lower()
        return self


def credential_digest(credential: ContentCredential) -> str:
    return sha256(canonical_json(credential.model_dump(mode="json")).encode("utf-8")).hexdigest()


def credential_signing_payload(credential: ContentCredential) -> bytes:
    data = credential.model_dump(mode="json")
    data.pop("signature")
    return canonical_json(data).encode("utf-8")


def verify_credential_signature(
    credential: ContentCredential,
    *,
    public_key_b64: str,
) -> bool:
    if credential.signature_algorithm != "ed25519":
        return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        public_key = base64.b64decode(public_key_b64, validate=True)
        signature = base64.b64decode(credential.signature, validate=True)
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            signature, credential_signing_payload(credential)
        )
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def validate_content_credential(
    credential: ContentCredential | None,
    *,
    artifact_sha256: str,
    trusted_issuer: bool = False,
    conflicting: bool = False,
    signature_valid: bool | None = None,
) -> CredentialStatus:
    if credential is None:
        return CredentialStatus.ABSENT
    if credential.artifact_sha256 != artifact_sha256:
        return CredentialStatus.INVALID
    if conflicting:
        return CredentialStatus.CONFLICTING
    if signature_valid is False:
        return CredentialStatus.INVALID
    if not trusted_issuer:
        return CredentialStatus.VALID
    return CredentialStatus.TRUSTED


def credential_to_evidence(
    credential: ContentCredential,
    *,
    artifact_sha256: str,
    status: CredentialStatus,
    signature_valid: bool | None = None,
) -> Evidence:
    """Expose C2PA as provenance evidence, never as an authenticity verdict."""
    if status in {CredentialStatus.INVALID, CredentialStatus.CONFLICTING}:
        signal_status = SignalStatus.FAILED
    else:
        signal_status = SignalStatus.AVAILABLE

    return Evidence(
        evidence_id=f"c2pa:{credential.manifest_id}",
        source_group=f"c2pa:{credential.issuer}",
        signal="content_credentials",
        status=signal_status,
        kind=EvidenceKind.FACT,
        summary=f"Content Credential status: {status.value}",
        details={
            "manifest_id": credential.manifest_id,
            "issuer": credential.issuer,
            "artifact_sha256": credential.artifact_sha256,
            "credential_digest": credential_digest(credential),
            "credential_status": status.value,
            "signature_valid": signature_valid,
            "artifact_bound": credential.artifact_sha256 == artifact_sha256,
        },
    )
