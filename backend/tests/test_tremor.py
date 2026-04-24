"""Unit tests for TremorAnalyzer.

Step 16: exercise the three signal paths — empty buffer, flat input, and a
synthetic sinusoid at a known frequency. Runs without MediaPipe installed,
because hand_tracker defers the mediapipe imports into HandTracker methods.
"""

from __future__ import annotations

import math

import pytest

from app.hand_tracker import TargetPoint
from app.tremor import MIN_SAMPLES_FOR_METRICS, TremorAnalyzer


def _target(x: float, y: float, diag: float = 0.3, hand: str = "Right") -> TargetPoint:
    return TargetPoint(x=x, y=y, bbox_diag=diag, handedness=hand)


def test_empty_buffer_returns_zero_metrics() -> None:
    analyzer = TremorAnalyzer()
    m = analyzer.metrics()
    assert m.level == 0.0
    assert m.magnitude == 0.0
    assert m.frequency == 0.0
    assert m.hand is None
    assert m.samples == 0


def test_too_few_samples_returns_zero_magnitude_but_reports_hand() -> None:
    analyzer = TremorAnalyzer()
    for i in range(MIN_SAMPLES_FOR_METRICS - 1):
        analyzer.push(_target(0.5, 0.5), ts=i * 0.033)
    m = analyzer.metrics()
    assert m.magnitude == 0.0
    assert m.frequency == 0.0
    assert m.hand == "Right"
    assert m.samples == MIN_SAMPLES_FOR_METRICS - 1


def test_flat_input_has_near_zero_magnitude() -> None:
    analyzer = TremorAnalyzer(window_seconds=2.0)
    fs = 30.0
    for i in range(60):
        analyzer.push(_target(0.5, 0.5), ts=i / fs)
    m = analyzer.metrics()
    assert m.magnitude < 1e-5
    assert m.samples > 0


def test_linear_drift_detrended_to_near_zero() -> None:
    analyzer = TremorAnalyzer(window_seconds=2.0)
    fs = 30.0
    # purely linear drift — detrender should remove it entirely
    for i in range(60):
        x = 0.3 + 0.005 * i
        y = 0.7 - 0.002 * i
        analyzer.push(_target(x, y), ts=i / fs)
    m = analyzer.metrics()
    assert m.magnitude < 1e-5


@pytest.mark.parametrize("freq_hz", [5.0, 8.0, 11.0])
def test_synthetic_sinusoid_is_detected(freq_hz: float) -> None:
    analyzer = TremorAnalyzer(window_seconds=2.0)
    fs = 60.0
    n = int(fs * 2)
    amplitude = 0.02  # normalized coords
    diag = 0.3
    for i in range(n):
        t = i / fs
        x = 0.5 + amplitude * math.sin(2 * math.pi * freq_hz * t)
        y = 0.5
        analyzer.push(_target(x, y, diag=diag), ts=t)

    m = analyzer.metrics()
    assert m.magnitude > 0.0
    # Frequency resolution is ~0.5 Hz for a 2s window.
    assert abs(m.frequency - freq_hz) <= 1.0
    # RMS of sin(2πft) with amplitude A is A/√2; after /diag it's A/(√2·diag).
    expected_magnitude = amplitude / (math.sqrt(2) * diag)
    assert abs(m.magnitude - expected_magnitude) / expected_magnitude < 0.15


def test_reset_clears_buffer() -> None:
    analyzer = TremorAnalyzer()
    for i in range(30):
        analyzer.push(_target(0.5, 0.5), ts=i * 0.033)
    analyzer.reset()
    assert analyzer.metrics().samples == 0


def test_window_expiry_drops_old_samples() -> None:
    analyzer = TremorAnalyzer(window_seconds=1.0)
    for i in range(120):
        analyzer.push(_target(0.5, 0.5), ts=i * 0.05)
    m = analyzer.metrics()
    # 1s window at 20Hz should retain ~21 samples, not 120.
    assert m.samples <= 25
