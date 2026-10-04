from __future__ import annotations

import uuid
import hashlib
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from .api_keys import registry as api_key_registry
from .attestation import artifact_digest, verify_artifact_signature
from .key_registry import registry as key_registry
from .receipt_store import store as receipt_store
from .rate_limit import receipt_read_limiter

router = APIRouter(prefix="/agent")


def _canonical_response_digest(payload: dict) -> str:
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def require_agent_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()
    record = api_key_registry.authenticate(token or "", "agent:trust")
    if record is None:
        raise HTTPException(status_code=401, detail="Invalid, expired, revoked, or insufficient API key")
    return record


@router.get("/trust/{verification_id}")
def get_agent_trust(
    verification_id: str,
    request: Request,
    _api_key=Depends(require_agent_key),
) -> dict:
    try:
        uuid.UUID(verification_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="verification_id must be a UUID") from exc

    identity = request.client.host if request.client else "unknown"
    decision = receipt_read_limiter.check(identity)
    if not decision.allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )

    artifact = receipt_store.get(verification_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Verification receipt not found")

    cryptographic_valid = bool(
        artifact.signature and artifact.signature_algorithm and verify_artifact_signature(artifact)
    )
    key_id = None
    key_status = "unknown"
    if artifact.signature_algorithm and ":" in artifact.signature_algorithm:
        algorithm, key_id = artifact.signature_algorithm.split(":", 1)
        record = key_registry.get(key_id)
        if record and record.algorithm == algorithm:
            key_status = record.status

    response = {
        "protocol": "REALITYX-AI-AGENT-TRUST",
        "protocol_version": "1.0",
        "verification_id": verification_id,
        "result": artifact.result.value,
        "confidence": artifact.confidence,
        "media_sha256": artifact.media_sha256,
        "evidence_graph_digest": artifact.evidence_graph_digest,
        "policy_version": artifact.policy_version,
        "risk_level": artifact.risk_level,
        "authority_status": artifact.authority_status,
        "independent_source_count": artifact.independent_source_count,
        "conflict": artifact.conflict,
        "receipt_digest": artifact_digest(artifact),
        "cryptographic_valid": cryptographic_valid,
        "key_id": key_id,
        "key_status": key_status,
        "trust_document_digest": key_registry.public_document_digest(),
        "decision_boundary": "uncertainty_preserved",
    }
    response["issued_at"] = datetime.now(timezone.utc).isoformat()
    response["response_digest"] = _canonical_response_digest(response)
    return response
