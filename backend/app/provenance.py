"""Evidence provenance and lineage primitives.

Provenance is supporting evidence, not automatic proof of authenticity.
Untrusted claims remain claims until cryptographically and semantically validated.
"""

from __future__ import annotations

from enum import StrEnum
from hashlib import sha256
from typing import Iterable

from .attestation import canonical_json

from pydantic import BaseModel, ConfigDict, Field


class ProvenanceSource(StrEnum):
    USER_UPLOAD = "user_upload"
    PUBLIC_STANDARD = "public_standard"
    DOCUMENTED_API = "documented_public_api"
    CONTENT_CREDENTIALS = "content_credentials"
    CRYPTOGRAPHIC_SIGNATURE = "cryptographic_signature"
    ENGINE_OBSERVATION = "engine_observation"


class ProvenanceTrust(StrEnum):
    UNASSESSED = "unassessed"
    SUPPORTED = "supported"
    VERIFIED = "verified"
    INVALID = "invalid"
    CONFLICTING = "conflicting"


class ProvenanceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: ProvenanceSource
    trust: ProvenanceTrust = ProvenanceTrust.UNASSESSED
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    claim: str = Field(min_length=1, max_length=1000)
    issuer: str | None = Field(default=None, max_length=256)
    evidence_ids: list[str] = Field(default_factory=list)


def provenance_digest(records: Iterable[ProvenanceRecord]) -> str:
    canonical = sorted(
        (record.model_dump(mode="json") for record in records),
        key=lambda item: canonical_json(item),
    )
    payload = canonical_json(canonical).encode("utf-8")
    return sha256(payload).hexdigest()


def assess_provenance(records: list[ProvenanceRecord]) -> ProvenanceTrust:
    """Return the aggregate provenance state without creating an authenticity verdict."""
    if not records:
        return ProvenanceTrust.UNASSESSED
    trusts = {record.trust for record in records}
    if ProvenanceTrust.CONFLICTING in trusts:
        return ProvenanceTrust.CONFLICTING
    if ProvenanceTrust.INVALID in trusts:
        return ProvenanceTrust.INVALID
    if ProvenanceTrust.VERIFIED in trusts:
        return ProvenanceTrust.VERIFIED
    if ProvenanceTrust.SUPPORTED in trusts:
        return ProvenanceTrust.SUPPORTED
    return ProvenanceTrust.UNASSESSED
