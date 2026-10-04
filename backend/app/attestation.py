from __future__ import annotations

import hashlib
import json
from typing import Any

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
            exclude={"signature", "signature_algorithm"},
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
