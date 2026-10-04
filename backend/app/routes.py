import hashlib
import uuid
from fastapi import APIRouter, File, Header, HTTPException, Request, UploadFile
from starlette.concurrency import run_in_threadpool
from .attestation import build_artifact
from .contracts import VerificationResponse
from .idempotency import store
from .pipeline import run_signal_pipeline
from .evidence_fusion import fuse_evidence
from .rate_limit import image_verify_limiter
from .risk_assessment import assess_risk
from .verification_policy import evaluate_verification
from .security import MAX_UPLOAD_BYTES, inspect_image, _magic_type
from .receipt_store import store as receipt_store
from .professional_store import store as professional_store
from .signing import sign_artifact

router = APIRouter()
ALLOWED_FORMATS = {"jpeg", "png", "webp"}


@router.post("/verify/image", response_model=VerificationResponse)
async def verify_image(
    request: Request,
    file: UploadFile = File(...),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> VerificationResponse:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key is required")

    identity = request.client.host if request.client else "unknown"
    decision = image_verify_limiter.check(identity)
    if not decision.allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many verification requests; please try again later.",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )
    try:
        uuid.UUID(idempotency_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Idempotency-Key must be a UUID") from exc

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload exceeds maximum size")

    kind = _magic_type(data)
    if kind not in ALLOWED_FORMATS:
        raise HTTPException(status_code=415, detail="Unsupported or invalid image format")

    declared_mime = (file.content_type or "").lower()
    expected_mime = {"jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}[kind]
    if declared_mime and declared_mime != expected_mime:
        raise HTTPException(status_code=415, detail="Declared content type does not match image format")

    fingerprint = hashlib.sha256(data).hexdigest()
    try:
        inspect_image(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        cached, claimed = store.claim(idempotency_key, fingerprint)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if cached is not None:
        return VerificationResponse.model_validate(cached)

    if not claimed:
        raise HTTPException(
            status_code=409,
            detail="Verification with this Idempotency-Key is already in progress; please retry.",
            headers={"Retry-After": "2"},
        )

    try:
        verification_id = str(uuid.uuid4())
        signals = await run_in_threadpool(run_signal_pipeline, data, verification_id, fingerprint)
        decision = fuse_evidence(signals)
        risk = assess_risk(signals)
        unified = evaluate_verification(
            signals,
            fusion_result=decision.result,
            fusion_confidence=decision.confidence,
            fusion_conflict=decision.conflict,
        )
        response = VerificationResponse(
            verification_id=verification_id,
            sha256=fingerprint,
            result=unified.result,
            confidence=unified.confidence,
            signals=signals,
            evidence=decision.evidence,
            risk_domain=risk.domain.value,
            risk_level=risk.level.value,
            risk_action=risk.action.value,
            risk_confidence=risk.confidence,
            risk_reasons=list(unified.risk.reasons),
            policy_version=unified.policy_version,
            authority_status=unified.authority_status.value,
            independent_source_count=unified.independent_source_count,
            conflict=unified.conflict,
            evidence_graph_digest=unified.evidence_graph_digest,
        )
        receipt_store.put(sign_artifact(build_artifact(response)))
        professional_store.put(response)
        store.put(idempotency_key, fingerprint, response.model_dump())
        return response
    except Exception:
        store.release(idempotency_key, fingerprint)
        raise
