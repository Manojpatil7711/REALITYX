"""Evidence provenance and lineage primitives.

Provenance is supporting evidence, not automatic proof of authenticity.
Untrusted claims remain claims until cryptographically and semantically validated.
"""

from __future__ import annotations

from enum import StrEnum
from hashlib import sha256
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field

from .attestation import canonical_json


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


class SourcePlatform(StrEnum):
    UNKNOWN = "unknown"
    USER_PROVIDED = "user_provided"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    X = "x"
    REDDIT = "reddit"
    WEB = "web"
    OTHER = "other"


class SourceConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class SourceProvenance(BaseModel):
    """Universal origin claim for media, documents and URLs.

    A source account is only reported when supported by evidence. It never
    turns a likely source into a confirmed original creator by itself.
    """

    model_config = ConfigDict(extra="forbid")
    platform: SourcePlatform = SourcePlatform.UNKNOWN
    source_url: str | None = Field(default=None, max_length=2048)
    source_user_or_account: str | None = Field(default=None, max_length=256)
    first_known_appearance: str | None = Field(default=None, max_length=128)
    confidence: SourceConfidence = SourceConfidence.UNKNOWN
    evidence_ids: list[str] = Field(default_factory=list)
    original_creator_confirmed: bool = False


def source_provenance_digest(provenance: SourceProvenance) -> str:
    return sha256(canonical_json(provenance.model_dump(mode="json"))).hexdigest()


def provenance_digest(records: Iterable[ProvenanceRecord]) -> str:
    canonical = sorted(
        (record.model_dump(mode="json") for record in records),
        key=lambda item: canonical_json(item),
    )
    payload = canonical_json(canonical)
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
