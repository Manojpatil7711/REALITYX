from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .contracts import Evidence, VerificationArtifact, VerificationResponse


def canonical_json(value: Any) -> bytes:
    """Serialize receipt data deterministically for hashing and signatures."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def evidence_hash(evidence: list[Evidence]) -> str:
    payload = [item.model_dump(mode="json", exclude_none=True) for item in evidence]
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def artifact_payload(artifact: VerificationArtifact) -> bytes:
    """Return the exact unsigned payload used by receipt digests/signatures."""
    return canonical_json(
        artifact.model_dump(
            mode="json",
            exclude={"signature"},
        )
    )


def artifact_digest(artifact: VerificationArtifact) -> str:
    """Return a stable SHA-256 digest for the unsigned receipt payload."""
    return hashlib.sha256(artifact_payload(artifact)).hexdigest()


def build_artifact(response: VerificationResponse) -> VerificationArtifact:
    if not response.evidence_graph_digest:
        raise ValueError("Verification response is missing evidence graph digest")
    return VerificationArtifact(
        verification_id=response.verification_id,
        media_sha256=response.sha256,
        result=response.result,
        confidence=response.confidence,
        engine_version=response.engine_version,
        evidence_hash=evidence_hash(response.evidence),
        evidence_graph_digest=response.evidence_graph_digest,
        policy_version=response.policy_version,
        risk_domain=response.risk_domain,
        risk_level=response.risk_level,
        authority_status=response.authority_status,
        independent_source_count=response.independent_source_count,
        conflict=response.conflict,
    )


def verify_artifact_signature(artifact: VerificationArtifact) -> bool:
    """Verify an Ed25519 receipt against its registered active public key."""
    if artifact.signature_algorithm is None or artifact.signature is None:
        return False
    prefix, sep, key_id = artifact.signature_algorithm.partition(":")
    if prefix != "Ed25519" or not sep or not key_id:
        return False
    try:
        record = __import__("app.key_registry", fromlist=["registry"]).registry.require_active(key_id)
        public_raw = base64.b64decode(record.public_key, validate=True)
        signature = base64.b64decode(artifact.signature, validate=True)
        Ed25519PublicKey.from_public_bytes(public_raw).verify(signature, artifact_payload(artifact))
        return True
    except (InvalidSignature, RuntimeError, ValueError, TypeError):
        return False
