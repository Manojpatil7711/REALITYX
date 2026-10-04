import io

import numpy as np
from PIL import Image

from app.engines.base import EngineContext
from app.forensic_features import ForensicFeatureEngine


def _png() -> bytes:
    image = Image.fromarray(
        np.arange(16 * 12 * 3, dtype=np.uint8).reshape((12, 16, 3))
    )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_forensic_features_are_deterministic_and_non_verdict():
    data = _png()
    engine = ForensicFeatureEngine()
    context = EngineContext("test-verification", "unused")

    first = engine.analyze(data, context)
    second = engine.analyze(data, context)

    assert first == second
    assert first["status"] == "available"
    assert first["analysis_scope"] == "forensic_features_only"
    assert first["verdict_policy"] == "never_direct"
    assert first["confidence"] == 1.0
    assert "verdict" not in first


def test_forensic_features_contain_spatial_signals():
    result = ForensicFeatureEngine().analyze(
        _png(), EngineContext("test-verification", "unused")
    )
    features = result["features"]
    assert set(features) == {
        "gray_mean",
        "gray_std",
        "gray_skewness",
        "gray_kurtosis_excess",
        "horizontal_gradient_mean",
        "vertical_gradient_mean",
        "dynamic_range",
    }
    assert all(np.isfinite(value) for value in features.values())
