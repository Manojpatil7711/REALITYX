from __future__ import annotations

import hashlib
import json
from typing import Any

from .contracts import Evidence, VerificationArtifact, VerificationResponse


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def evidence_hash(evidence: list[Evidence]) -> str:
    payload = [item.model_dump(mode="json", exclude_none=True) for item in evidence]
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def build_artifact(response: VerificationResponse) -> VerificationArtifact:
    return VerificationArtifact(
        verification_id=response.verification_id,
        media_sha256=response.sha256,
        result=response.result,
        confidence=response.confidence,
        engine_version=response.engine_version,
        evidence_hash=evidence_hash(response.evidence),
    )
