"""Tremor analyzer.

Step 15 (this commit): estimate the dominant tremor frequency. Take the
rfft of both detrended x and y signals, sum their magnitude spectra, and
find the peak within 3-15 Hz. This brackets essential tremor (~4-12 Hz)
and parkinsonian resting tremor (~3-6 Hz). Sample rate is derived from
the timestamps in the buffer (webcam frames aren't perfectly uniform but
it's close enough for a PoC).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import detrend

from app.hand_tracker import TargetPoint

MIN_SAMPLES_FOR_METRICS = 10
TREMOR_BAND_HZ: tuple[float, float] = (3.0, 15.0)


@dataclass(frozen=True)
class TremorSample:
    ts: float  # monotonic seconds since capture start
    x: float
    y: float
    bbox_diag: float
    hand: str


@dataclass(frozen=True)
class TremorMetrics:
    level: float  # clamped [0, 1] normalized against TREMOR_THRESHOLD (wired in step 19)
    magnitude: float  # scale-invariant RMS (step 14)
    frequency: float  # Hz, dominant freq in 3-15 Hz band (step 15)
    hand: str | None
    samples: int


class TremorAnalyzer:
    """Holds a ~N-second rolling buffer of (ts, x, y, bbox_diag) samples."""

    def __init__(self, window_seconds: float = 2.0) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self._window = window_seconds
        self._samples: deque[TremorSample] = deque()

    @property
    def window_seconds(self) -> float:
        return self._window

    def push(self, target: TargetPoint | None, ts: float) -> None:
        """Add a sample (or skip if no hand detected) and drop expired entries."""
        if target is not None:
            self._samples.append(
                TremorSample(
                    ts=ts,
                    x=target.x,
                    y=target.y,
                    bbox_diag=target.bbox_diag,
                    hand=target.handedness,
                )
            )
        cutoff = ts - self._window
        while self._samples and self._samples[0].ts < cutoff:
            self._samples.popleft()

    def reset(self) -> None:
        self._samples.clear()

    def metrics(self) -> TremorMetrics:
        """Compute RMS magnitude of the detrended trajectory."""
        if not self._samples:
            return TremorMetrics(level=0.0, magnitude=0.0, frequency=0.0, hand=None, samples=0)

        hand = self._samples[-1].hand
        n = len(self._samples)
        if n < MIN_SAMPLES_FOR_METRICS:
            return TremorMetrics(level=0.0, magnitude=0.0, frequency=0.0, hand=hand, samples=n)

        xs = np.fromiter((s.x for s in self._samples), dtype=np.float32, count=n)
        ys = np.fromiter((s.y for s in self._samples), dtype=np.float32, count=n)
        ts = np.fromiter((s.ts for s in self._samples), dtype=np.float64, count=n)
        diags = np.fromiter((s.bbox_diag for s in self._samples), dtype=np.float32, count=n)

        dx = detrend(xs, type="linear")
        dy = detrend(ys, type="linear")
        rms = float(np.sqrt(np.mean(dx * dx + dy * dy)))
        diag_median = float(np.median(diags))
        magnitude = rms / diag_median if diag_median > 1e-6 else 0.0
        frequency = _dominant_frequency(dx, dy, ts)

        return TremorMetrics(
            level=0.0,  # normalized level is wired in step 19 alongside env config
            magnitude=magnitude,
            frequency=frequency,
            hand=hand,
            samples=n,
        )


def _dominant_frequency(dx: np.ndarray, dy: np.ndarray, ts: np.ndarray) -> float:
    n = dx.size
    duration = float(ts[-1] - ts[0])
    if duration <= 0.0 or n < 4:
        return 0.0
    fs = (n - 1) / duration
    freqs = rfftfreq(n, d=1.0 / fs)
    spectrum = np.abs(rfft(dx)) + np.abs(rfft(dy))
    low, high = TREMOR_BAND_HZ
    band = (freqs >= low) & (freqs <= high)
    if not np.any(band):
        return 0.0
    band_freqs = freqs[band]
    band_spec = spectrum[band]
    return float(band_freqs[int(np.argmax(band_spec))])
