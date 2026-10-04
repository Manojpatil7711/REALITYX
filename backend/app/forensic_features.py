"""Deterministic forensic feature extraction for the REALITYX evidence layer.

This module deliberately produces observations, not authenticity verdicts.
Higher-level fusion may use these observations only when benchmarked and gated.
"""

from __future__ import annotations

import io
from typing import Any

import numpy as np
from PIL import Image

from .engines.base import EngineContext, SignalEngine


class ForensicFeatureEngine(SignalEngine):
    name = "forensic_features"
    version = "0.1.0"

    def analyze(self, data: bytes, context: EngineContext) -> dict[str, Any]:
        del context
        with Image.open(io.BytesIO(data)) as image:
            rgb = np.asarray(image.convert("RGB"), dtype=np.float32)

        gray = rgb.mean(axis=2)
        mean = float(gray.mean())
        std = float(gray.std())
        if std == 0.0:
            skewness = 0.0
            kurtosis_excess = 0.0
        else:
            z = (gray - mean) / std
            skewness = float(np.mean(z**3))
            kurtosis_excess = float(np.mean(z**4) - 3.0)

        # Simple first-order spatial discontinuity measurements. These are
        # evidence features only; thresholds must be benchmarked before use.
        horizontal = np.abs(np.diff(gray, axis=1))
        vertical = np.abs(np.diff(gray, axis=0))

        return {
            "status": "available",
            "summary": "Deterministic pixel-distribution and spatial-consistency features extracted.",
            "confidence": 1.0,
            "features": {
                "gray_mean": round(mean, 6),
                "gray_std": round(std, 6),
                "gray_skewness": round(skewness, 6),
                "gray_kurtosis_excess": round(kurtosis_excess, 6),
                "horizontal_gradient_mean": round(float(horizontal.mean()), 6),
                "vertical_gradient_mean": round(float(vertical.mean()), 6),
                "dynamic_range": round(float(rgb.max() - rgb.min()), 6),
            },
            "analysis_scope": "forensic_features_only",
            "verdict_policy": "never_direct",
        }
