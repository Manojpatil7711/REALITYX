from app.capability_watch import compare, snapshot
from app.engines.base import SignalEngine


class EngineA(SignalEngine):
    name = "engine-a"
    version = "1.0.0"

    def analyze(self, data: bytes, context):
        return {"status": "available"}


class EngineB(SignalEngine):
    name = "engine-b"
    version = "1.0.0"

    def analyze(self, data: bytes, context):
        return {"status": "available"}


def test_snapshot_is_stable_for_same_registry():
    first = snapshot((EngineA, EngineB), "1.0")
    second = snapshot((EngineB, EngineA), "1.0")

    assert first.fingerprint == second.fingerprint
    assert first.engines == second.engines


def test_compare_detects_added_engine_without_mutating_policy():
    expected = snapshot((EngineA,), "1.0")
    current = snapshot((EngineA, EngineB), "1.0")

    report = compare(expected, current)

    assert report["changed"] is True
    assert report["protocol_changed"] is False
    assert any(name == "engine-b" and version == "1.0.0" for name, version, _ in report["added"])
