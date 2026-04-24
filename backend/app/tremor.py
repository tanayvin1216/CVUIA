"""Tremor analyzer.

Step 14 (this commit): divide the RMS magnitude by the median hand-bbox
diagonal across the window. Both are in normalized MediaPipe coordinates,
so the result is dimensionless and scale-invariant — a hand held close to
the camera and a hand held far away produce the same number for the same
amount of shake.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np
from scipy.signal import detrend

from app.hand_tracker import TargetPoint

MIN_SAMPLES_FOR_METRICS = 10


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
        diags = np.fromiter((s.bbox_diag for s in self._samples), dtype=np.float32, count=n)
        dx = detrend(xs, type="linear")
        dy = detrend(ys, type="linear")
        rms = float(np.sqrt(np.mean(dx * dx + dy * dy)))
        diag_median = float(np.median(diags))
        magnitude = rms / diag_median if diag_median > 1e-6 else 0.0

        return TremorMetrics(
            level=0.0,  # normalized level is wired in step 19 alongside env config
            magnitude=magnitude,
            frequency=0.0,  # FFT arrives in step 15
            hand=hand,
            samples=n,
        )
