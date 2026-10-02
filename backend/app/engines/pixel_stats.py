from __future__ import annotations

import io
from typing import Any

import numpy as np
from PIL import Image

from .base import EngineContext, SignalEngine


class PixelStatisticsEngine(SignalEngine):
    """Deterministic pixel-distribution evidence; never claims authenticity."""

    name = "pixel_statistics"

    def analyze(self, data: bytes, context: EngineContext) -> dict[str, Any]:
        del context
        with Image.open(io.BytesIO(data)) as image:
            rgb = image.convert("RGB")
            array = np.asarray(rgb, dtype=np.float32)

        mean = array.mean(axis=(0, 1))
        std = array.std(axis=(0, 1))

        return {
            "status": "available",
            "summary": "पिक्सेल distribution आणि channel statistics मोजल्या गेल्या; हे स्वतःहून authenticity verdict नाही.",
            "mean_rgb": [round(float(value), 4) for value in mean],
            "std_rgb": [round(float(value), 4) for value in std],
            "dynamic_range": round(float(array.max() - array.min()), 4),
            "analysis_scope": "pixel_statistics_only",
        }
