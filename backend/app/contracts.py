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


class EvidenceStrength(StrEnum):
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"
    INSUFFICIENT = "insufficient"
    CONFLICTING = "conflicting"


class ProfessionalEvidenceStatus(StrEnum):
    STRONG = "STRONG"
    MEDIUM = "MEDIUM"
    WEAK = "WEAK"
    NEGATIVE = "NEGATIVE"
    CONFLICTING = "CONFLICTING"
    NOT_AVAILABLE = "NOT_AVAILABLE"


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


class VerificationArtifact(BaseModel):
    """Portable, signed-verification-ready receipt; not a legal certification."""
    model_config = ConfigDict(extra="forbid")
    artifact_version: str = "1.1"
    protocol_version: str = PROTOCOL_VERSION
    verification_id: str
    media_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    result: VerificationResult
    confidence: float = Field(ge=0.0, le=1.0)
    engine_version: str = ENGINE_VERSION
    evidence_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence_graph_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_version: str = "2050.1"
    risk_domain: str = "unknown"
    risk_level: str = "uncertain"
    authority_status: str = "not_required"
    independent_source_count: int = Field(default=0, ge=0)
    conflict: bool = False
    issuer: str = "REALITYX"
    signature_algorithm: str | None = None
    signature: str | None = None


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
    risk_domain: str = "unknown"
    risk_level: str = "uncertain"
    risk_action: str = "reverify"
    risk_confidence: float = 0.0
    risk_reasons: list[str] = Field(default_factory=list)
    policy_version: str = "2050.1"
    authority_status: str = "not_required"
    independent_source_count: int = 0
    conflict: bool = False
    evidence_graph_digest: str = Field(default="", pattern=r"^(|[0-9a-f]{64})$")


class ProfessionalEvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_id: str
    signal: str
    status: ProfessionalEvidenceStatus
    summary: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    engine_version: str | None = None
    location: str | None = None


class ProfessionalVerificationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_version: str = "1.0"
    verification_id: str
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    verdict: VerificationResult
    conclusion: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_strength: EvidenceStrength
    evidence: list[ProfessionalEvidenceItem]
    independent_source_count: int
    conflict: bool
    provenance_status: str
    protocol_version: str
    engine_version: str
    policy_version: str
    evidence_graph_digest: str = Field(default="", pattern=r"^(|[0-9a-f]{64})$")
    limitations: list[str] = Field(default_factory=list)
    receipt_status: str = "available"
