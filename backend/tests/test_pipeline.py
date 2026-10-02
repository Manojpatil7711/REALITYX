import time

from app import pipeline
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
