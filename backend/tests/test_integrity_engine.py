import hashlib
import io

from PIL import Image

from app.engines.base import EngineContext
from app.engines.integrity import IntegrityEngine


def _png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 6)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_integrity_engine_matches_context_hash():
    data = _png()
    result = IntegrityEngine().analyze(
        data,
        EngineContext(
            verification_id="v",
            media_sha256=hashlib.sha256(data).hexdigest(),
        ),
    )
    assert result["status"] == "available"
    assert result["confidence"] == 1.0
    assert result["sha256_matches_context"] is True
    assert result["format"] == "png"
    assert result["analysis_scope"] == "integrity_only"


def test_integrity_engine_detects_hash_mismatch():
    data = _png()
    result = IntegrityEngine().analyze(
        data,
        EngineContext(verification_id="v", media_sha256="0" * 64),
    )
    assert result["sha256_matches_context"] is False
