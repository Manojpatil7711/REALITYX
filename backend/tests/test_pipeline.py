import time

from app import pipeline
from app.contracts import EvidenceKind, SignalStatus, SignalVerdict
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


def test_pipeline_assigns_deterministic_evidence_identity(monkeypatch):
    class IdentityEngine(SignalEngine):
        name = "identity_test"

        def analyze(self, data, context):
            return {"status": "available", "summary": "test"}

    monkeypatch.setattr(pipeline, "ENGINE_REGISTRY", (IdentityEngine,))
    first = pipeline.run_signal_pipeline(b"data", "v1", "s")
    second = pipeline.run_signal_pipeline(b"data", "v2", "s")

    assert first[0].evidence_id == "identity_test"
    assert first[0].source_group == "identity_test"
    assert first[0].evidence_id == second[0].evidence_id


def test_pipeline_marks_timed_out_engine_as_failed(monkeypatch):
    class HangingEngine(SignalEngine):
        name = "hanging"

        def analyze(self, data, context):
            time.sleep(0.2)
            return {"status": "available", "summary": "late"}

    monkeypatch.setattr(pipeline, "ENGINE_REGISTRY", (HangingEngine,))
    monkeypatch.setattr(pipeline, "ENGINE_TIMEOUT_SECONDS", 0.02)

    started = time.perf_counter()
    evidence = pipeline.run_signal_pipeline(b"data", "v", "s")
    elapsed = time.perf_counter() - started

    assert elapsed < 0.1
    assert evidence[0].status is SignalStatus.FAILED
    assert evidence[0].details["error_code"] == "SIGNAL_TIMEOUT"
    assert evidence[0].verdict is None


def test_fact_engine_is_explicitly_classified():
    class FactEngine(SignalEngine):
        name = "fact_test"

        def analyze(self, data, context):
            return {"status": "available", "summary": "test", "confidence": 1.0}

    evidence = pipeline._run_engine(
        FactEngine,
        b"data",
        pipeline.EngineContext(verification_id="v", media_sha256="s"),
    )

    assert evidence.kind is EvidenceKind.FACT
    assert evidence.verdict is None


def test_engine_confidence_and_verdict_are_preserved():
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
    assert evidence.kind is EvidenceKind.VERDICT
    assert evidence.confidence == 0.83
    assert evidence.verdict is SignalVerdict.AUTHENTIC
    assert "verdict" not in evidence.details
