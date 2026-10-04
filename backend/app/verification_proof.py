"""Portable cryptographic proof for a REALITYX verification decision.

The proof binds the decision to its evidence-graph digest and policy version.
It contains no private key material and never upgrades an uncertain decision.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from .verification_policy import UnifiedVerificationDecision

PROOF_VERSION = "1.0"

@dataclass(frozen=True)
class VerificationProof:
    proof_version: str
    policy_version: str
    result: str
    confidence: float
    evidence_graph_digest: str
    independent_source_count: int
    conflict: bool
    proof_digest: str

def _payload(decision: UnifiedVerificationDecision) -> dict:
    return {
        "proof_version": PROOF_VERSION,
        "policy_version": decision.policy_version,
        "result": decision.result.value,
        "confidence": decision.confidence,
        "evidence_graph_digest": decision.evidence_graph_digest,
        "independent_source_count": decision.independent_source_count,
        "conflict": decision.conflict,
    }

def _digest(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()

def build_verification_proof(decision: UnifiedVerificationDecision) -> VerificationProof:
    payload = _payload(decision)
    return VerificationProof(**payload, proof_digest=_digest(payload))

def validate_verification_proof(proof: VerificationProof) -> bool:
    payload = {
        "proof_version": proof.proof_version,
        "policy_version": proof.policy_version,
        "result": proof.result,
        "confidence": proof.confidence,
        "evidence_graph_digest": proof.evidence_graph_digest,
        "independent_source_count": proof.independent_source_count,
        "conflict": proof.conflict,
    }
    return proof.proof_digest == _digest(payload)
