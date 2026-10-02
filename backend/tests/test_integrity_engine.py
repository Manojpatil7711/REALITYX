from app.engines.base import EngineContext
from app.engines.integrity import IntegrityEngine


def test_integrity_engine_matches_context_hash():
    data = b"fixture"
    result = IntegrityEngine().analyze(
        data,
        EngineContext(
            verification_id="v",
            media_sha256=__import__("hashlib").sha256(data).hexdigest(),
        ),
    )
    assert result["status"] == "available"
    assert result["confidence"] == 1.0
    assert result["sha256_matches_context"] is True
    assert result["analysis_scope"] == "integrity_only"


def test_integrity_engine_detects_hash_mismatch():
    result = IntegrityEngine().analyze(
        b"fixture",
        EngineContext(verification_id="v", media_sha256="0" * 64),
    )
    assert result["sha256_matches_context"] is False
