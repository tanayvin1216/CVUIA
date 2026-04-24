"""Webcam capture loop + MediaPipe inference + debug overlay.

Step 9 (this commit): render the 21-point hand skeleton and bounding box on
the cv2 debug window using overlays.draw_hands.
"""

from __future__ import annotations

import logging
import time

import cv2

from app.hand_tracker import HandTracker
from app.overlays import draw_hands

log = logging.getLogger(__name__)


def run_capture(camera_index: int = 0, window_name: str = "CVUIA — capture") -> None:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"could not open camera index {camera_index}")

    last_tick = time.perf_counter()
    fps_ema = 0.0
    ema_alpha = 0.1
    start = time.perf_counter()

    try:
        with HandTracker() as tracker:
            while True:
                ok, frame = cap.read()
                if not ok:
                    log.warning("dropped frame")
                    continue

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp_ms = int((time.perf_counter() - start) * 1000)
                hands = tracker.process(rgb, timestamp_ms)
                draw_hands(frame, hands)

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
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    run_capture()
