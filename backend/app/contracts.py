from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

PROTOCOL_VERSION = "1.0"
ENGINE_VERSION = "0.1.0"


class SignalStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


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


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signal: str
    status: SignalStatus
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
