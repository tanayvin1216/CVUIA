"""FastAPI entrypoint.

Step 17 (this commit): app factory + /health. The /ws/tremor WebSocket and
the capture thread hookup come in subsequent commits.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.schema import HealthPayload

log = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="CVUIA backend", version=__version__)
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

    return app


app = create_app()
