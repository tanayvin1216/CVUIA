"""FastAPI entrypoint.

Step 19 (this commit): runtime configuration is loaded from env vars
(app.config.settings). The magnitude → level mapping lives here: level is
clamp(magnitude / tremor_threshold, 0, 1), letting the frontend consume a
single normalized scalar.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect, WebSocketState

from app import __version__
from app.capture import run_capture
from app.config import settings
from app.hand_tracker import TargetPoint
from app.schema import HealthPayload, TremorPayload
from app.tremor import TremorAnalyzer

log = logging.getLogger(__name__)


class CaptureState:
    """Thread-safe container for analyzer state updated by the capture loop."""

    def __init__(self, window_seconds: float, threshold: float) -> None:
        self.analyzer = TremorAnalyzer(window_seconds=window_seconds)
        self.threshold = threshold
        self.latest_ts: float = 0.0
        self._lock = threading.Lock()

    def on_target(self, target: TargetPoint | None, ts: float, _frame_idx: int) -> None:
        with self._lock:
            self.analyzer.push(target, ts)
            self.latest_ts = ts

    def snapshot(self) -> TremorPayload:
        with self._lock:
            m = self.analyzer.metrics()
            ts = self.latest_ts
        level = 0.0 if self.threshold <= 0 else min(m.magnitude / self.threshold, 1.0)
        return TremorPayload(
            level=level,
            magnitude=m.magnitude,
            frequency=m.frequency,
            hand=m.hand,
            samples=m.samples,
            timestamp=ts,
        )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    state = CaptureState(
        window_seconds=settings.window_seconds,
        threshold=settings.tremor_threshold,
    )
    _app.state.capture = state

    def _target() -> None:
        try:
            run_capture(camera_index=settings.camera_index, on_target=state.on_target)
        except Exception:
            log.exception("capture thread crashed")

    thread = threading.Thread(target=_target, name="cvuia-capture", daemon=True)
    thread.start()
    log.info("capture thread started")
    try:
        yield
    finally:
        log.info("shutting down (capture thread is daemon; cv2 window closes with process)")


def create_app() -> FastAPI:
    app = FastAPI(title="CVUIA backend", version=__version__, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthPayload)
    async def health() -> HealthPayload:
        return HealthPayload(status="ok", version=__version__)

    @app.websocket("/ws/tremor")
    async def ws_tremor(ws: WebSocket) -> None:
        await ws.accept()
        state: CaptureState = ws.app.state.capture
        interval = 1.0 / settings.ws_rate_hz
        try:
            while ws.client_state == WebSocketState.CONNECTED:
                payload = state.snapshot()
                await ws.send_json(payload.model_dump())
                await asyncio.sleep(interval)
        except WebSocketDisconnect:
            pass
        except Exception:
            log.exception("ws_tremor loop error")
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.close()

    return app


app = create_app()
