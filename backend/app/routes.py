import hashlib
import uuid
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from .contracts import VerificationResponse
from .idempotency import store
from .pipeline import run_signal_pipeline
from .security import MAX_UPLOAD_BYTES, inspect_image, _magic_type

router = APIRouter()
ALLOWED_FORMATS = {"jpeg", "png", "webp"}

@router.post("/verify/image", response_model=VerificationResponse)
async def verify_image(
    file: UploadFile = File(...),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> VerificationResponse:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key is required")
    try:
        uuid.UUID(idempotency_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Idempotency-Key must be a UUID") from exc

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload exceeds maximum size")

    kind = _magic_type(data)
    if kind not in ALLOWED_FORMATS:
        raise HTTPException(status_code=415, detail="Unsupported or invalid image format")

    fingerprint = hashlib.sha256(data).hexdigest()
    try:
        cached = store.get(idempotency_key, fingerprint)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if cached is not None:
        return VerificationResponse.model_validate(cached)

    try:
        inspect_image(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    verification_id = str(uuid.uuid4())
    signals = run_signal_pipeline(data, verification_id, fingerprint)
    response = VerificationResponse(
        verification_id=verification_id,
        sha256=fingerprint,
        result="uncertain",
        confidence=0.0,
        signals=signals,
        evidence=[],
    )
    store.put(idempotency_key, fingerprint, response.model_dump())
    return response
