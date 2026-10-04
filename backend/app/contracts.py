from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

PROTOCOL_VERSION = "1.0"
ENGINE_VERSION = "0.1.0"


class SignalStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


class EvidenceKind(StrEnum):
    FACT = "fact"
    VERDICT = "verdict"


class SignalVerdict(StrEnum):
    AUTHENTIC = "authentic"
    VERIFIED = "verified"
    MANIPULATED = "manipulated"
    AI_GENERATED = "ai_generated"
    INAUTHENTIC = "inauthentic"


class VerificationResult(StrEnum):
    VERIFIED = "verified"
    INAUTHENTIC = "inauthentic"
    UNCERTAIN = "uncertain"


class VerificationArtifact(BaseModel):
    """Portable, signed-verification-ready receipt; not a legal certification."""
    model_config = ConfigDict(extra="forbid")
    artifact_version: str = "1.0"
    protocol_version: str = PROTOCOL_VERSION
    verification_id: str
    media_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    result: VerificationResult
    confidence: float = Field(ge=0.0, le=1.0)
    engine_version: str = ENGINE_VERSION
    evidence_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    issuer: str = "REALITYX"
    signature_algorithm: str | None = None
    signature: str | None = None


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_id: str = Field(default="")
    source_group: str = Field(default="")
    parent_evidence_ids: list[str] = Field(default_factory=list)
    signal: str
    status: SignalStatus
    kind: EvidenceKind = EvidenceKind.FACT
    summary: str
    details: dict = Field(default_factory=dict)
    verdict: SignalVerdict | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    latency_ms: float | None = Field(default=None, ge=0.0)


class VerificationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    protocol_version: str = PROTOCOL_VERSION
    engine_version: str = ENGINE_VERSION
    verification_id: str
    sha256: str
    result: VerificationResult
    confidence: float
    signals: list[Evidence]
    evidence: list[Evidence]
