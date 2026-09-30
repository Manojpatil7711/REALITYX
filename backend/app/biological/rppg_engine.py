from __future__ import annotations

import numpy as np


def _safe_normalize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    scale = np.std(x)
    if not np.isfinite(scale) or scale < 1e-12:
        return np.zeros_like(x)
    return (x - np.mean(x)) / scale


def estimate_pulse_signal(rgb_frames: np.ndarray, fps: float) -> dict:
    """Estimate a pulse-related signal from tracked skin-region RGB means.

    This is forensic signal extraction, not a medical measurement.
    Input shape: [frames, 3] with RGB means from a stable skin region.
    """
    frames = np.asarray(rgb_frames, dtype=np.float64)
    if frames.ndim != 2 or frames.shape[1] != 3:
        raise ValueError("rgb_frames must have shape [frames, 3]")
    if not np.isfinite(frames).all() or fps <= 0:
        raise ValueError("Invalid physiological signal input")
    if len(frames) < max(30, int(fps * 4)):
        return {"status": "unavailable", "reason": "not_enough_temporal_data"}

    mean = np.mean(frames, axis=0)
    mean[mean == 0] = 1.0
    normalized = frames / mean
    r, g, b = normalized.T

    # Chrominance projection: suppress common illumination changes.
    x = 3.0 * r - 2.0 * g
    y = 1.5 * r + g - 1.5 * b
    alpha = np.std(x) / (np.std(y) + 1e-12)
    signal = _safe_normalize(x - alpha * y)

    # Degenerate color relationships can cancel the projection; retain a
    # conservative temporal fallback rather than inventing a physiological signal.
    if np.std(signal) < 1e-6:
        signal = _safe_normalize(g)

    return {
        "status": "available",
        "samples": int(len(signal)),
        "fps": float(fps),
        "signal": signal.tolist(),
        "method": "chrominance_temporal_projection",
    }
