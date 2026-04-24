# CVUIA

Tremor-adaptive UI, driven by a camera that watches the user's hand.

A proof of concept: a Python service reads webcam frames, runs MediaPipe hand
tracking, estimates tremor magnitude + frequency, and streams the metrics over a
WebSocket to a React demo UI that adapts — larger targets, more spacing, smoothed
input, debounced clicks — to make itself usable for someone with a hand tremor.

Status: **in development.** See [`PLAN.md`](./PLAN.md) for the full plan and
[`WIP.md`](./WIP.md) for live progress.

## Stack
- **Backend (Python):** OpenCV + MediaPipe HandLandmarker + NumPy/SciPy + FastAPI
- **Frontend (TypeScript):** Vite + React 18 + TailwindCSS
- **Transport:** WebSocket, JSON at ~20 Hz

## Quick start
*(Populated at step 34 — the repo is still being scaffolded.)*
