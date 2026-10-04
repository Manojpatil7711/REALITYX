"""Provider-neutral external verification connector boundary.

External providers supply evidence; REALITYX remains the decision authority.
Credentials are references only and are never stored or serialized here.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
import hashlib, json
from typing import Mapping, Protocol
from .contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict

CONNECTOR_PROTOCOL_VERSION = "1.0"

class ProviderStatus(StrEnum):
    ACTIVE="active"
    DISABLED="disabled"
    REVOKED="revoked"

class ExternalVerificationStatus(StrEnum):
    VERIFIED="verified"
    NOT_VERIFIED="not_verified"
    UNCERTAIN="uncertain"
    UNAVAILABLE="unavailable"

@dataclass(frozen=True)
class ProviderRequest:
    provider_id: str
    subject_reference: str
    operation: str
    idempotency_key: str

@dataclass(frozen=True)
class ProviderResponse:
    provider_id: str
    provider_version: str
    status: ExternalVerificationStatus
    summary: str
    reference: str = ""
    confidence: float | None = None
    signal: str = "external_authority"
    schema_version: str = "1.0"

@dataclass(frozen=True)
class ExternalVerificationResult:
    provider_id: str
    status: ExternalVerificationStatus
    evidence: Evidence
    provider_version: str
    schema_version: str

class ProviderConnector(Protocol):
    provider_id: str
    provider_version: str
    def verify(self, request: ProviderRequest) -> ProviderResponse: ...

def normalize_response(response: ProviderResponse) -> ExternalVerificationResult:
    confidence = response.confidence
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise ValueError("provider confidence must be between 0 and 1")
    if response.status is ExternalVerificationStatus.VERIFIED:
        kind, verdict, status = EvidenceKind.VERDICT, SignalVerdict.VERIFIED, SignalStatus.AVAILABLE
    elif response.status is ExternalVerificationStatus.NOT_VERIFIED:
        kind, verdict, status = EvidenceKind.VERDICT, SignalVerdict.INAUTHENTIC, SignalStatus.AVAILABLE
    elif response.status is ExternalVerificationStatus.UNCERTAIN:
        kind, verdict, status = EvidenceKind.FACT, None, SignalStatus.AVAILABLE
    else:
        kind, verdict, status = EvidenceKind.FACT, None, SignalStatus.UNAVAILABLE
    evidence = Evidence(
        evidence_id=f"provider:{response.provider_id}:{response.signal}",
        source_group=f"provider:{response.provider_id}",
        signal=response.signal,
        status=status,
        kind=kind,
        summary=response.summary,
        details={"provider_reference": response.reference,
                 "provider_version": response.provider_version,
                 "schema_version": response.schema_version},
        verdict=verdict,
        confidence=confidence,
    )
    return ExternalVerificationResult(response.provider_id, response.status, evidence,
                                      response.provider_version, response.schema_version)

@dataclass(frozen=True)
class ConnectorRecord:
    provider_id: str
    provider_version: str
    status: ProviderStatus
    connector: ProviderConnector

class ConnectorRegistry:
    def __init__(self) -> None:
        self._records: dict[str, ConnectorRecord] = {}
    def register(self, record: ConnectorRecord) -> None:
        if not record.provider_id.strip():
            raise ValueError("provider_id cannot be empty")
        if record.provider_id in self._records:
            raise ValueError("provider already registered")
        self._records[record.provider_id] = record
    def get(self, provider_id: str) -> ConnectorRecord | None:
        return self._records.get(provider_id)
    def usable(self, provider_id: str) -> bool:
        record = self.get(provider_id)
        return record is not None and record.status is ProviderStatus.ACTIVE
    def digest(self) -> str:
        payload=[{"provider_id":r.provider_id,"provider_version":r.provider_version,"status":r.status.value}
                 for r in sorted(self._records.values(), key=lambda x:x.provider_id)]
        return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
