"""cv2 drawing helpers for the debug window.

Step 9 (this commit): draw the 21-point hand skeleton plus an axis-aligned
bounding box for each detected hand, color-coded by handedness.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.hand_tracker import HandObservation

# Standard MediaPipe hand topology (21 landmarks).
HAND_CONNECTIONS: tuple[tuple[int, int], ...] = (
    # wrist -> finger MCPs
    (0, 1), (0, 5), (0, 9), (0, 13), (0, 17),
    # thumb
    (1, 2), (2, 3), (3, 4),
    # index
    (5, 6), (6, 7), (7, 8),
    # middle
    (9, 10), (10, 11), (11, 12),
    # ring
    (13, 14), (14, 15), (15, 16),
    # pinky
    (17, 18), (18, 19), (19, 20),
    # palm crossbars
    (5, 9), (9, 13), (13, 17),
)

# BGR — cv2 uses BGR natively.
COLOR_RIGHT = (120, 230, 255)  # warm for right
COLOR_LEFT = (255, 180, 120)  # cool for left
COLOR_LANDMARK = (60, 60, 60)
COLOR_BBOX = (40, 200, 120)


def draw_hands(frame: np.ndarray, hands: list[HandObservation]) -> None:
    """Draw skeleton + bbox for each hand. Mutates `frame` in place."""
    h, w = frame.shape[:2]
    for hand in hands:
        color = COLOR_RIGHT if hand.handedness == "Right" else COLOR_LEFT
        pts = _to_pixels(hand.landmarks, w, h)
        _draw_skeleton(frame, pts, color)
        _draw_landmarks(frame, pts)
        _draw_bbox(frame, pts, hand.handedness, hand.score)


def _to_pixels(landmarks: np.ndarray, w: int, h: int) -> np.ndarray:
    xy = landmarks[:, :2].copy()
    xy[:, 0] *= w
    xy[:, 1] *= h
    return xy.astype(np.int32)


def _draw_skeleton(frame: np.ndarray, pts: np.ndarray, color: tuple[int, int, int]) -> None:
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, tuple(pts[a]), tuple(pts[b]), color, 2, cv2.LINE_AA)


def _draw_landmarks(frame: np.ndarray, pts: np.ndarray) -> None:
    for x, y in pts:
        cv2.circle(frame, (int(x), int(y)), 3, COLOR_LANDMARK, -1, cv2.LINE_AA)


def _draw_bbox(
    frame: np.ndarray,
    pts: np.ndarray,
    handedness: str,
    score: float,
) -> None:
    x0, y0 = pts.min(axis=0)
    x1, y1 = pts.max(axis=0)
    pad = 8
    x0, y0 = max(0, int(x0) - pad), max(0, int(y0) - pad)
    x1, y1 = int(x1) + pad, int(y1) + pad
    cv2.rectangle(frame, (x0, y0), (x1, y1), COLOR_BBOX, 1, cv2.LINE_AA)
    label = f"{handedness} {score:.2f}"
    cv2.putText(
        frame,
        label,
        (x0, max(0, y0 - 6)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        COLOR_BBOX,
        1,
        cv2.LINE_AA,
    )
