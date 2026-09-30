from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceLimits:
    max_upload_bytes: int = 25 * 1024 * 1024
    max_decode_pixels: int = 80_000_000
    max_decode_width: int = 12_000
    max_decode_height: int = 12_000
    max_processing_seconds: float = 30.0


def validate_upload_size(size: int, limits: ResourceLimits = ResourceLimits()) -> None:
    if size < 0:
        raise ValueError("Upload size cannot be negative")
    if size > limits.max_upload_bytes:
        raise ValueError("Upload exceeds maximum size")


def validate_processing_budget(
    elapsed_seconds: float,
    limits: ResourceLimits = ResourceLimits(),
) -> None:
    if elapsed_seconds < 0:
        raise ValueError("Processing time cannot be negative")
    if elapsed_seconds > limits.max_processing_seconds:
        raise TimeoutError("Verification processing budget exceeded")
