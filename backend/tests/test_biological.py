import numpy as np
from app.biological.rppg_engine import estimate_pulse_signal
from app.biological.pulse_analysis import analyze_pulse_signal

def test_rppg_extracts_periodic_signal():
    fps = 30.0
    t = np.arange(180) / fps
    pulse = 0.02 * np.sin(2 * np.pi * 1.2 * t)
    frames = np.column_stack([
        0.55 + pulse,
        0.40 + pulse * 0.7,
        0.32 + pulse * 0.4,
    ])
    extracted = estimate_pulse_signal(frames, fps)
    assert extracted["status"] == "available"
    analysis = analyze_pulse_signal(extracted["signal"], fps)
    assert analysis["status"] == "available"
    assert 60 < analysis["estimated_bpm"] < 90

def test_rppg_rejects_short_sequence():
    result = estimate_pulse_signal(np.ones((10, 3)), 30.0)
    assert result["status"] == "unavailable"
