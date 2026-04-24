"""Tremor analyzer.

Step 12 (this commit): scaffolding — a time-windowed rolling buffer of tracked
fingertip positions. Metric computation (RMS, normalization, FFT) arrives in
steps 13-15.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from app.hand_tracker import TargetPoint


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
        """Scaffold — returns zeros until real analysis is wired in step 13+."""
        if not self._samples:
            return TremorMetrics(level=0.0, magnitude=0.0, frequency=0.0, hand=None, samples=0)
        return TremorMetrics(
            level=0.0,
            magnitude=0.0,
            frequency=0.0,
            hand=self._samples[-1].hand,
            samples=len(self._samples),
        )
