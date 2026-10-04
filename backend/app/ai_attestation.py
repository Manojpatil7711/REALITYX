"""Provider-neutral AI attestation boundary for REALITYX.

This is a protocol boundary, not a claim that every external AI provider is
trusted. Providers submit evidence; REALITYX decides trust and verification.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from .contracts import Evidence
from .verification_policy import POLICY_VERSION

ATTESTATION_VERSION = "1.0"

class ProviderTrust(StrEnum):
    UNTRUSTED = "untrusted"
    REGISTERED = "registered"
    ATTESTED = "attested"
    REVOKED = "revoked"

@dataclass(frozen=True)
class AIProvider:
    provider_id: str
    provider_version: str
    trust: ProviderTrust = ProviderTrust.UNTRUSTED

@dataclass(frozen=True)
class AttestedEvidence:
    provider: AIProvider
    evidence: Evidence
    evidence_digest: str
    protocol_version: str = ATTESTATION_VERSION
    policy_version: str = POLICY_VERSION

def evidence_digest(evidence: Evidence) -> str:
    payload = evidence.model_dump(mode="json", exclude_none=True)
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()

def attest_evidence(provider: AIProvider, evidence: Evidence) -> AttestedEvidence:
    if provider.trust is ProviderTrust.REVOKED:
        raise ValueError("revoked provider cannot attest evidence")
    return AttestedEvidence(provider=provider, evidence=evidence,
                            evidence_digest=evidence_digest(evidence))

def validate_attestation(attested: AttestedEvidence) -> bool:
    if attested.provider.trust is ProviderTrust.REVOKED:
        return False
    return attested.evidence_digest == evidence_digest(attested.evidence)
