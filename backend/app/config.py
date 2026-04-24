"""Runtime configuration loaded from environment variables.

All vars are prefixed `CVUIA_`. Defaults are tuned for a typical laptop webcam
+ essential-tremor-range detection; the threshold in particular is empirical
and can be swept during a tuning pass.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    camera_index: int
    target_fps: int
    window_seconds: float
    tremor_threshold: float  # normalized magnitude that maps to level = 1.0
    ws_rate_hz: float


def load_settings() -> Settings:
    s = Settings(
        camera_index=int(os.environ.get("CVUIA_CAMERA_INDEX", "0")),
        target_fps=int(os.environ.get("CVUIA_TARGET_FPS", "30")),
        window_seconds=float(os.environ.get("CVUIA_WINDOW_SECONDS", "2.0")),
        tremor_threshold=float(os.environ.get("CVUIA_TREMOR_THRESHOLD", "0.04")),
        ws_rate_hz=float(os.environ.get("CVUIA_WS_RATE_HZ", "20")),
    )
    log.info(
        "loaded settings: camera=%d fps=%d window=%.1fs threshold=%.3f ws_rate=%.1fHz",
        s.camera_index,
        s.target_fps,
        s.window_seconds,
        s.tremor_threshold,
        s.ws_rate_hz,
    )
    return s


settings: Settings = load_settings()
