from __future__ import annotations
import numpy as np

def analyze_pulse_signal(signal: list[float], fps: float) -> dict:
    """Extract a pulse-rate range from a forensic pulse-related signal.

    The result is a consistency signal. It is not a clinical diagnosis.
    """
    x = np.asarray(signal, dtype=np.float64)
    if x.ndim != 1 or len(x) < 30 or fps <= 0 or not np.isfinite(x).all():
        return {"status": "unavailable", "reason": "insufficient_or_invalid_signal"}

    x = x - np.mean(x)
    spectrum = np.abs(np.fft.rfft(x))
    frequencies = np.fft.rfftfreq(len(x), d=1.0 / fps)
    band = (frequencies >= 0.7) & (frequencies <= 3.5)
    if not np.any(band):
        return {"status": "unavailable", "reason": "no_physiological_band"}

    band_power = spectrum[band]
    idx = int(np.argmax(band_power))
    peak_hz = float(frequencies[band][idx])
    bpm = peak_hz * 60.0
    relative_peak = float(band_power[idx] / (np.mean(band_power) + 1e-12))

    return {
        "status": "available",
        "estimated_bpm": round(bpm, 2),
        "peak_strength": round(relative_peak, 4),
        "interpretation": "pulse-related periodicity detected",
    }
