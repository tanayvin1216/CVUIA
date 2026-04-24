"""Webcam capture loop + MediaPipe inference + debug overlay.

Step 11 (this commit): decouple capture from downstream analysis. run_capture
now accepts an optional callback invoked every frame with the current target
point (or None), a monotonic timestamp, and a frame index. The TremorAnalyzer
(step 12) and the WebSocket broadcaster (step 18) will plug in here without
further changes to the loop.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

import cv2

from app.hand_tracker import HandTracker, TargetPoint, select_target
from app.overlays import draw_hands

log = logging.getLogger(__name__)

TARGET_COLOR = (0, 220, 255)

FrameCallback = Callable[[TargetPoint | None, float, int], None]


def run_capture(
    camera_index: int = 0,
    window_name: str = "CVUIA — capture",
    on_target: FrameCallback | None = None,
) -> None:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"could not open camera index {camera_index}")

    last_tick = time.perf_counter()
    fps_ema = 0.0
    ema_alpha = 0.1
    start = time.perf_counter()
    frame_idx = 0

    try:
        with HandTracker() as tracker:
            while True:
                ok, frame = cap.read()
                if not ok:
                    log.warning("dropped frame")
                    continue

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                elapsed_s = time.perf_counter() - start
                timestamp_ms = int(elapsed_s * 1000)
                hands = tracker.process(rgb, timestamp_ms)
                draw_hands(frame, hands)

                target = select_target(hands)
                if target is not None:
                    h, w = frame.shape[:2]
                    tx, ty = int(target.x * w), int(target.y * h)
                    cv2.circle(frame, (tx, ty), 10, TARGET_COLOR, 2, cv2.LINE_AA)
                    cv2.circle(frame, (tx, ty), 2, TARGET_COLOR, -1, cv2.LINE_AA)

                if on_target is not None:
                    try:
                        on_target(target, elapsed_s, frame_idx)
                    except Exception:
                        log.exception("on_target callback raised")

                now = time.perf_counter()
                dt = now - last_tick
                last_tick = now
                instant_fps = 1.0 / dt if dt > 0 else 0.0
                fps_ema = (
                    instant_fps
                    if fps_ema == 0.0
                    else (1 - ema_alpha) * fps_ema + ema_alpha * instant_fps
                )

                cv2.putText(
                    frame,
                    f"{fps_ema:5.1f} fps  hands={len(hands)}",
                    (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (50, 220, 120),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                frame_idx += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    run_capture()
