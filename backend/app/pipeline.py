import logging
import time
from .contracts import Evidence, SignalStatus
from .engines import ENGINE_REGISTRY, EngineContext

logger = logging.getLogger("realityx.pipeline")

def run_signal_pipeline(data: bytes, verification_id: str, media_sha256: str) -> list[Evidence]:
    context = EngineContext(verification_id=verification_id, media_sha256=media_sha256)
    results: list[Evidence] = []
    for engine_type in ENGINE_REGISTRY:
        engine = engine_type()
        started = time.perf_counter()
        try:
            result = engine.analyze(data, context)
            status = SignalStatus(result.get("status", "available"))
            results.append(Evidence(
                signal=engine.name,
                status=status,
                summary=result.get("summary", "तपासणी पूर्ण झाली."),
                details={k: v for k, v in result.items() if k not in {"status", "summary"}},
                latency_ms=(time.perf_counter() - started) * 1000,
            ))
            logger.info("signal completed", extra={
                "verification_id": verification_id,
                "signal_name": engine.name,
                "status": status.value,
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            })
        except Exception:
            elapsed = (time.perf_counter() - started) * 1000
            results.append(Evidence(
                signal=engine.name,
                status=SignalStatus.FAILED,
                summary="ही तपासणी सध्या पूर्ण झाली नाही; उपलब्ध पुराव्यावरच निष्कर्ष दिला आहे.",
                latency_ms=elapsed,
            ))
            logger.exception("signal failed", extra={
                "verification_id": verification_id,
                "signal_name": engine.name,
                "status": "failed",
                "latency_ms": round(elapsed, 3),
                "error_code": "SIGNAL_FAILURE",
            })
    return results
