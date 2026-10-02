from __future__ import annotations

import hashlib
from typing import Any

from PIL import Image

from .base import EngineContext, SignalEngine


class IntegrityEngine(SignalEngine):
    name = "integrity"

    def analyze(self, data: bytes, context: EngineContext) -> dict[str, Any]:
        # This engine reports deterministic file/container facts only. It never
        # turns successful decoding into an authenticity claim.
        image = Image.open(__import__("io").BytesIO(data))
        image_format = (image.format or "unknown").lower()
        width, height = image.size

        return {
            "status": "available",
            "summary": "फाइलचा deterministic fingerprint आणि decoded container integrity तपासली गेली.",
            "confidence": 1.0,
            "sha256_matches_context": hashlib.sha256(data).hexdigest() == context.media_sha256,
            "format": image_format,
            "width": width,
            "height": height,
            "bytes": len(data),
            "analysis_scope": "integrity_only",
        }
