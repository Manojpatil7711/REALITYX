from __future__ import annotations

import io
from typing import Any

from PIL import Image

from .base import EngineContext, SignalEngine


class StructureEngine(SignalEngine):
    name = "image_structure"

    def analyze(self, data: bytes, context: EngineContext) -> dict[str, Any]:
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            mode = image.mode
            format_name = (image.format or "unknown").lower()
            frame_count = getattr(image, "n_frames", 1)
            has_alpha = "A" in image.getbands()

        return {
            "status": "available",
            "summary": "इमेजची decoded संरचना, format, dimensions आणि frame metadata तपासली गेली.",
            "confidence": 1.0,
            "format": format_name,
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 6),
            "mode": mode,
            "has_alpha": has_alpha,
            "frame_count": frame_count,
            "analysis_scope": "structural_only",
        }
