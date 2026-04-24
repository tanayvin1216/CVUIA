"""Pydantic wire-format models for the WebSocket stream."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TremorPayload(BaseModel):
    """One tremor update pushed to the frontend over /ws/tremor."""

    level: float = Field(ge=0.0, le=1.0, description="Normalized tremor level, clamped [0, 1]")
    magnitude: float = Field(ge=0.0, description="Scale-invariant RMS magnitude")
    frequency: float = Field(ge=0.0, description="Dominant frequency (Hz) in 3-15 Hz band")
    hand: str | None = Field(default=None, description="'Left' / 'Right' / null when no hand detected")
    samples: int = Field(ge=0, description="Number of samples in the current analysis window")
    timestamp: float = Field(ge=0.0, description="Monotonic seconds since capture start")


class HealthPayload(BaseModel):
    status: str
    version: str
