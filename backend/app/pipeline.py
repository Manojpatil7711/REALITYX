import logging
import time
from concurrent.futures import ThreadPoolExecutor

from .contracts import Evidence, SignalStatus
from .engines import ENGINE_REGISTRY, EngineContext

logger = logging.getLogger("realityx.pipeline")

_MAX_WORKERS = max(1, min(8, len(ENGINE_REGISTRY)))


def _run_engine(engine_type, data: bytes, context: EngineContext) -> Evidence:
    engine = engine_type()
    started = time.perf_counter()
    try:
        result = engine.analyze(data, context)
        status = SignalStatus(result.get("status", "available"))
        elapsed = (time.perf_counter() - started) * 1000
        evidence = Evidence(
            signal=engine.name,
            status=status,
            summary=result.get("summary", "तपासणी पूर्ण झाली."),
            details={k: v for k, v in result.items() if k not in {"status", "summary"}},
            latency_ms=elapsed,
        )
        logger.info(
            "signal completed",
            extra={
                "verification_id": context.verification_id,
                "signal_name": engine.name,
                "status": status.value,
                "latency_ms": round(elapsed, 3),
            },
        )
        return evidence
    except Exception:
        elapsed = (time.perf_counter() - started) * 1000
        logger.exception(
            "signal failed",
            extra={
                "verification_id": context.verification_id,
                "signal_name": engine.name,
                "status": "failed",
                "latency_ms": round(elapsed, 3),
                "error_code": "SIGNAL_FAILURE",
            },
        )
        return Evidence(
            signal=engine.name,
            status=SignalStatus.FAILED,
            summary="ही तपासणी सध्या पूर्ण झाली नाही; उपलब्ध पुराव्यावरच निष्कर्ष दिला आहे.",
            latency_ms=elapsed,
        )


def run_signal_pipeline(data: bytes, verification_id: str, media_sha256: str) -> list[Evidence]:
    context = EngineContext(verification_id=verification_id, media_sha256=media_sha256)

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS, thread_name_prefix="rx-signal") as executor:
        futures = [
            executor.submit(_run_engine, engine_type, data, context)
            for engine_type in ENGINE_REGISTRY
        ]
        results = [future.result() for future in futures]

    return results
