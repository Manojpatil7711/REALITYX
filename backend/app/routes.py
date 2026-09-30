import hashlib
import uuid
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from .security import MAX_UPLOAD_BYTES, inspect_image

router = APIRouter()

@router.post("/verify/image")
async def verify_image(
    file: UploadFile = File(...),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key is required")
    try:
        uuid.UUID(idempotency_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Idempotency-Key must be a UUID") from exc

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload exceeds maximum size")

    verification_id = str(uuid.uuid4())
    digest = hashlib.sha256(data).hexdigest()

    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Unsupported image media type")

    inspection = inspect_image(data)
    return {
        "verification_id": verification_id,
        "sha256": digest,
        "result": "uncertain",
        "signals": inspection,
        "evidence": [],
    }
