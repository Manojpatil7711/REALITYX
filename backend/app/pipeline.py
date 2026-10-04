import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from .contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict
from .engines import ENGINE_REGISTRY, EngineContext

logger = logging.getLogger("realityx.pipeline")

ENGINE_TIMEOUT_SECONDS = 10.0


def _failed_evidence(engine_type, elapsed: float, error_code: str) -> Evidence:
    return Evidence(
        evidence_id=engine_type.name,
        source_group=engine_type.name,
        signal=engine_type.name,
        status=SignalStatus.FAILED,
        summary="ही तपासणी सध्या पूर्ण झाली नाही; उपलब्ध पुराव्यावरच निष्कर्ष दिला आहे.",
        details={"error_code": error_code},
        latency_ms=elapsed,
    )


def _run_engine(engine_type, data: bytes, context: EngineContext) -> Evidence:
    engine = engine_type()
    started = time.perf_counter()
    evidence_id = engine.name
    try:
        result = engine.analyze(data, context)
        status = SignalStatus(result.get("status", "available"))
        raw_verdict = result.get("verdict")
        verdict = SignalVerdict(raw_verdict) if raw_verdict is not None else None
        elapsed = (time.perf_counter() - started) * 1000
        evidence = Evidence(
            evidence_id=evidence_id,
            source_group=engine.name,
            signal=engine.name,
            status=status,
            kind=EvidenceKind.VERDICT if verdict is not None else EvidenceKind.FACT,
            summary=result.get("summary", "तपासणी पूर्ण झाली."),
            details={k: v for k, v in result.items() if k not in {"status", "summary", "confidence", "verdict"}},
            verdict=verdict,
            confidence=result.get("confidence"),
            latency_ms=elapsed,
        )
        logger.info(
            "signal completed",
            extra={
                "verification_id": context.verification_id,
                "signal_name": engine.name,
                "status": status.value,
                "kind": evidence.kind.value,
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
        return _failed_evidence(engine_type, elapsed, "SIGNAL_FAILURE")


def run_signal_pipeline(data: bytes, verification_id: str, media_sha256: str) -> list[Evidence]:
    context = EngineContext(verification_id=verification_id, media_sha256=media_sha256)
    engine_types = tuple(ENGINE_REGISTRY)
    if not engine_types:
        return []

    max_workers = max(1, min(8, len(engine_types)))
    executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="rx-signal")
    futures = [executor.submit(_run_engine, engine_type, data, context) for engine_type in engine_types]
    results: list[Evidence] = []

    try:
        for engine_type, future in zip(engine_types, futures):
            started = time.perf_counter()
            try:
                results.append(future.result(timeout=ENGINE_TIMEOUT_SECONDS))
            except TimeoutError:
                elapsed = (time.perf_counter() - started) * 1000
                logger.error(
                    "signal timed out",
                    extra={
                        "verification_id": verification_id,
                        "signal_name": engine_type.name,
                        "status": "failed",
                        "error_code": "SIGNAL_TIMEOUT",
                        "timeout_seconds": ENGINE_TIMEOUT_SECONDS,
                    },
                )
                results.append(_failed_evidence(engine_type, elapsed, "SIGNAL_TIMEOUT"))
            except Exception:
                elapsed = (time.perf_counter() - started) * 1000
                logger.exception(
                    "signal future failed",
                    extra={
                        "verification_id": verification_id,
                        "signal_name": engine_type.name,
                        "status": "failed",
                        "error_code": "SIGNAL_FUTURE_FAILURE",
                    },
                )
                results.append(_failed_evidence(engine_type, elapsed, "SIGNAL_FUTURE_FAILURE"))
        return results
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
