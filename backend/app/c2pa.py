"""Provider-neutral Content Credentials / C2PA trust boundary.

Credentials are provenance evidence. A valid credential never becomes an
authenticity verdict by itself; artifact binding and trust state remain explicit.
"""

from __future__ import annotations

from enum import StrEnum
from hashlib import sha256

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .attestation import canonical_json


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


def validate_content_credential(
    credential: ContentCredential | None,
    *,
    artifact_sha256: str,
    trusted_issuer: bool = False,
    conflicting: bool = False,
) -> CredentialStatus:
    if credential is None:
        return CredentialStatus.ABSENT
    if credential.artifact_sha256 != artifact_sha256:
        return CredentialStatus.INVALID
    if conflicting:
        return CredentialStatus.CONFLICTING
    if not trusted_issuer:
        return CredentialStatus.VALID
    return CredentialStatus.TRUSTED
