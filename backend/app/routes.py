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

# Container signatures are intentionally conservative: recognizing a valid
# container is structural evidence only, never proof of authenticity.
MEDIA_FORMATS = {"pdf", "zip", "mp4", "mov", "webm", "mp3", "wav", "flac", "ogg"}


def _media_format(data: bytes) -> str | None:
    if data.startswith(b"%PDF-"):
        return "pdf"
    if data.startswith((b"PK\\x03\\x04", b"PK\\x05\\x06", b"PK\\x07\\x08")):
        return "zip"
    if len(data) >= 12 and data[4:8] == b"ftyp":
        major_brand = data[8:12]
        return "mov" if major_brand in {b"qt  "} else "mp4"
    if data.startswith(b"\\x1a\\x45\\xdf\\xa3"):
        return "webm"
    if data.startswith(b"ID3") or (len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
        return "mp3"
    if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WAVE":
        return "wav"
    if data.startswith(b"fLaC"):
        return "flac"
    if data.startswith(b"OggS"):
        return "ogg"
    return None


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


@router.post("/verify/media", response_model=VerificationResponse)
async def verify_media(
    request: Request,
    file: UploadFile = File(...),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> VerificationResponse:
    """Perform safe container-level verification for non-image uploads.

    This deliberately reports UNCERTAIN for authenticity until a media-specific
    forensic engine is available; it never upgrades structural validity into
    proof of origin or authenticity.
    """
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key is required")
    try:
        uuid.UUID(idempotency_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Idempotency-Key must be a UUID") from exc

    identity = request.client.host if request.client else "unknown"
    decision = image_verify_limiter.check(identity)
    if not decision.allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many verification requests; please try again later.",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload exceeds maximum size")

    kind = _media_format(data)
    if kind not in MEDIA_FORMATS:
        raise HTTPException(status_code=415, detail="Unsupported or invalid media container")

    fingerprint = hashlib.sha256(data).hexdigest()
    declared_mime = (file.content_type or "").lower()
    expected = {
        "pdf": "application/pdf",
        "zip": "application/zip",
        "mp4": "video/mp4",
        "mov": "video/quicktime",
        "webm": "video/webm",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "flac": "audio/flac",
        "ogg": "audio/ogg",
    }[kind]
    if declared_mime and declared_mime != expected:
        raise HTTPException(status_code=415, detail="Declared content type does not match media container")

    cached, claimed = store.claim(idempotency_key, fingerprint)
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
        evidence = Evidence(
            evidence_id="container-integrity",
            source_group="container-integrity",
            signal="container-integrity",
            status=SignalStatus.AVAILABLE,
            kind=EvidenceKind.FACT,
            summary="File container signature is structurally recognized; authenticity is not established.",
            details={"format": kind, "authenticity_engine": "not_connected"},
            confidence=0.25,
        )
        response = VerificationResponse(
            verification_id=verification_id,
            sha256=fingerprint,
            result="uncertain",
            confidence=0.25,
            signals=[evidence],
            evidence=[evidence],
            risk_domain="digital_media",
            risk_level="uncertain",
            risk_action="reverify",
            risk_confidence=0.25,
            risk_reasons=["Media-specific forensic verification is not connected yet."],
            authority_status="not_required",
            independent_source_count=0,
            conflict=False,
        )
        decision = fuse_evidence([evidence])
        response = response.model_copy(update={
            "evidence_graph_digest": decision.evidence_graph_digest,
        })
        receipt_store.put(sign_artifact(build_artifact(response)))
        professional_store.put(response)
        store.put(idempotency_key, fingerprint, response.model_dump())
        return response
    except Exception:
        store.release(idempotency_key, fingerprint)
        raise
