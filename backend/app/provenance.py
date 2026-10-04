"""Evidence provenance and lineage primitives.

Provenance is supporting evidence, not automatic proof of authenticity.
Untrusted claims remain claims until cryptographically and semantically validated.
"""
from __future__ import annotations

import json
from enum import StrEnum
from hashlib import sha256
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


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


def build_video_source_provenance(
    *,
    platform: SourcePlatform,
    source_url: str | None = None,
    source_user_or_account: str | None = None,
    first_known_appearance: str | None = None,
    confidence: SourceConfidence = SourceConfidence.UNKNOWN,
    evidence_ids: list[str] | None = None,
    original_creator_confirmed: bool = False,
) -> SourceProvenance:
    """Create a conservative video origin record.

    A discovered account is not treated as the original creator unless the
    caller supplies explicit supporting evidence and sets confirmation true.
    """
    evidence = list(evidence_ids or [])
    if original_creator_confirmed and not evidence:
        raise ValueError("creator confirmation requires evidence_ids")
    if source_user_or_account is None and original_creator_confirmed:
        raise ValueError("creator confirmation requires a source account")
    return SourceProvenance(
        platform=platform,
        source_url=source_url,
        source_user_or_account=source_user_or_account,
        first_known_appearance=first_known_appearance,
        confidence=confidence,
        evidence_ids=evidence,
        original_creator_confirmed=original_creator_confirmed,
    )


def source_provenance_digest(provenance: SourceProvenance) -> str:
    return sha256(canonical_json(provenance.model_dump(mode="json"))).hexdigest()


def provenance_digest(records: Iterable[ProvenanceRecord]) -> str:
    canonical = sorted((record.model_dump(mode="json") for record in records), key=canonical_json)
    return sha256(canonical_json(canonical)).hexdigest()


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
