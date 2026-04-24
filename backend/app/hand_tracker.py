"""MediaPipe HandLandmarker wrapper.

Step 8 (this commit): download + load the MediaPipe hand-landmarker model and run
it per frame. Produces a list of detected hands, each with 21 normalized
landmarks. Drawing and downstream analysis are handled by later commits.

Uses VIDEO running-mode: synchronous calls, timestamp-ordered, benefits from
MediaPipe's internal temporal smoothing without the complexity of LIVE_STREAM
async callbacks.
"""

from __future__ import annotations

import logging
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"


INDEX_FINGERTIP = 8


@dataclass(frozen=True)
class HandObservation:
    """One detected hand for a single frame."""

    handedness: str  # "Left" or "Right" (as labeled by MediaPipe, mirrored for selfie view)
    score: float
    landmarks: np.ndarray  # shape (21, 3), normalized [0, 1] x,y,z


@dataclass(frozen=True)
class TargetPoint:
    """Tracked point on the dominant hand, used by the tremor analyzer."""

    x: float  # normalized [0, 1]
    y: float  # normalized [0, 1]
    bbox_diag: float  # normalized — diagonal of hand bbox; used for scale-invariant tremor
    handedness: str


def select_target(hands: list[HandObservation], prefer: str = "Right") -> TargetPoint | None:
    """Pick the dominant hand's index fingertip + bbox diagonal.

    Strategy: prefer the hand labeled `prefer` (default "Right"); if absent, use the
    highest-score hand. Returns None when no hands are detected.
    """
    if not hands:
        return None
    chosen = next((h for h in hands if h.handedness == prefer), None)
    if chosen is None:
        chosen = max(hands, key=lambda h: h.score)
    tip = chosen.landmarks[INDEX_FINGERTIP]
    xy = chosen.landmarks[:, :2]
    diag = float(np.linalg.norm(xy.max(axis=0) - xy.min(axis=0)))
    return TargetPoint(
        x=float(tip[0]),
        y=float(tip[1]),
        bbox_diag=diag,
        handedness=chosen.handedness,
    )


def ensure_model(path: Path = MODEL_PATH) -> Path:
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    log.info("downloading MediaPipe hand_landmarker model to %s", path)
    urllib.request.urlretrieve(MODEL_URL, path)  # noqa: S310 - fixed Google CDN URL
    return path


class HandTracker:
    """Synchronous wrapper around mp.tasks.vision.HandLandmarker in VIDEO mode."""

    def __init__(self, num_hands: int = 2, min_detection_confidence: float = 0.5) -> None:
        # Lazy imports: module loads without mediapipe so the pure-Python types
        # below (and the TremorAnalyzer tests) remain importable in environments
        # where mediapipe isn't installed.
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        model_path = ensure_model()
        base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_detection_confidence,
        )
        self._landmarker = mp_vision.HandLandmarker.create_from_options(options)

    def process(self, frame_rgb: np.ndarray, timestamp_ms: int) -> list[HandObservation]:
        import mediapipe as mp

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        return _to_observations(result)

    def close(self) -> None:
        self._landmarker.close()

    def __enter__(self) -> "HandTracker":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _to_observations(result) -> list[HandObservation]:  # noqa: ANN001 - mediapipe type
    observations: list[HandObservation] = []
    if not result.hand_landmarks:
        return observations
    for landmarks, handedness in zip(result.hand_landmarks, result.handedness, strict=False):
        arr = np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32)
        top = handedness[0] if handedness else None
        observations.append(
            HandObservation(
                handedness=top.category_name if top else "Unknown",
                score=float(top.score) if top else 0.0,
                landmarks=arr,
            )
        )
    return observations
