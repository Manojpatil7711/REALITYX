import time

from app import pipeline
from app.contracts import SignalStatus
from app.engines.base import SignalEngine


def test_independent_engines_run_concurrently(monkeypatch):
    class SlowA(SignalEngine):
        name = "slow_a"

        def analyze(self, data, context):
            time.sleep(0.05)
            return {"status": "available", "summary": "a"}

    class SlowB(SignalEngine):
        name = "slow_b"

        def analyze(self, data, context):
            time.sleep(0.05)
            return {"status": "available", "summary": "b"}

    monkeypatch.setattr(pipeline, "ENGINE_REGISTRY", (SlowA, SlowB))
    started = time.perf_counter()
    results = pipeline.run_signal_pipeline(b"test", "verification", "sha")
    elapsed = time.perf_counter() - started

    assert {item.signal for item in results} == {"slow_a", "slow_b"}
    assert elapsed < 0.09


def test_engine_confidence_is_preserved():
    class ConfidenceEngine(SignalEngine):
        name = "confidence_test"

        def analyze(self, data, context):
            return {
                "status": "available",
                "summary": "test",
                "confidence": 0.83,
                "verdict": "authentic",
            }

    evidence = pipeline._run_engine(
        ConfidenceEngine,
        b"data",
        pipeline.EngineContext(verification_id="v", media_sha256="s"),
    )

    assert evidence.status is SignalStatus.AVAILABLE
    assert evidence.confidence == 0.83
    assert evidence.details["verdict"] == "authentic"
