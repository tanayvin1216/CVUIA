# CVUIA — Tremor-Adaptive UI (PoC)

## Vision
A side-mounted laptop webcam watches the user's hand. A Python service analyzes hand
landmarks in real time, estimates tremor magnitude + dominant frequency, and streams
the metrics to a browser-based demo UI that adapts in response — larger targets, more
spacing, smoothed input, debounced clicks — to make the interface usable for someone
with a hand tremor.

## Stack (deliberately split, not monolithic)
- **Python backend (CV + analysis):** OpenCV (capture), MediaPipe HandLandmarker
  (21-point hand pose), NumPy + SciPy (detrend, RMS, FFT), FastAPI + `websockets`
  (push metrics).
- **TypeScript/React frontend (adaptive demo UI):** Vite + React 18 + TailwindCSS.
  Consumes the WebSocket stream.
- **Transport:** WebSocket, JSON frames at ~15–30 Hz.
- **Tooling:** `ruff` (Python), `biome` (JS), shared `.gitignore`, root `Makefile`.

Two languages, two runtimes, one clean wire protocol. No ML training, no DB, no auth.

## Architecture

```
┌────────────────────────┐    WebSocket JSON     ┌────────────────────────┐
│  Python (backend/)     │  {level, magnitude,   │  React (frontend/)     │
│                        │   frequency, hand,    │                        │
│  webcam → OpenCV       │   timestamp} @ ~20Hz  │  TremorContext         │
│  → MediaPipe Hands     │ ───────────────────▶  │  ↓                     │
│  → TremorAnalyzer      │                       │  AdaptiveButton        │
│  → FastAPI WS          │                       │  (size/spacing/        │
│  + debug cv2 window    │                       │   smoothing/debounce)  │
└────────────────────────┘                       └────────────────────────┘
```

### Tremor metric
1. Track a stable landmark per frame (index fingertip or palm center, dominant hand).
2. Buffer last ~2 s (~40 frames at 20 fps).
3. Detrend (subtract moving average) to isolate oscillatory component.
4. `magnitude = RMS of detrended signal` (pixels → normalized by hand bbox diagonal so
   distance-to-camera doesn't skew it).
5. `frequency = argmax(FFT)` in the 3–15 Hz band (essential tremor ~4–12 Hz).
6. `level = clamp(magnitude / threshold, 0, 1)` — threshold is a tunable constant.
7. Expose to UI as `{ level, magnitude, frequency, hand }`.

### Adaptation mapping (frontend)
- `level = 0` → buttons 1.0×, no debounce, no smoothing, baseline spacing.
- `level = 1` → buttons 1.8×, 250 ms click debounce, EMA pointer smoothing (α = 0.25),
  spacing 1.5×.
- Linearly interpolate between. Manual override slider for testing.

## Acceptance Criteria
1. `backend/` runs via `uvicorn app.main:app --reload`; opens a cv2 debug window
   showing live landmarks + current metrics.
2. `frontend/` runs via `npm run dev`; connects to the backend WS and renders live
   tremor level within 1 s of connection.
3. Shaking the hand in frame visibly raises the tremor level. Holding still returns to
   near-zero within ~2 s.
4. Demo number pad buttons visibly scale + space out when tremor is high; revert when
   steady.
5. Clicks under tremor are smoothed/debounced (measurable: fewer accidental multi-taps
   when shaking).
6. Manual override slider in the debug panel forces `level` so the UI can be demoed
   without an actual tremor.
7. Every step below ships as one atomic commit on `main`, pushed to
   `github.com/tanayvin1216/CVUIA.git`. Conventional commit messages, no AI
   co-author.

## Non-Goals
- Medical-grade tremor classification.
- Persistent users, auth, or cloud deployment.
- Mobile / touch platforms.
- Multi-hand fusion — pick dominant hand and move on.
- Full accessibility audit beyond target sizing.

## Steps — 32 atomic commits, each pushed individually

### Phase 0 — Repo bootstrap (3)
1. `chore: initial commit` — `.gitignore`, `README.md` stub, planning docs
   (`PLAN.md`, `WIP.md`, `LEARNINGS.md`). `git init`, add remote, push `main`.
2. `chore: add backend directory skeleton` — `backend/app/__init__.py`,
   `backend/tests/__init__.py`, placeholder `backend/README.md`.
3. `chore: add frontend directory skeleton` — `frontend/.gitkeep`, placeholder
   `frontend/README.md`.

### Phase 1 — Backend scaffolding (3)
4. `chore(backend): pyproject.toml with pinned deps` — opencv-python, mediapipe,
   numpy, scipy, fastapi, uvicorn, websockets, pytest, ruff.
5. `chore(backend): ruff config + pytest config`.
6. `chore: root Makefile` — `make run-backend`, `make run-frontend`, `make lint`,
   `make test`.

### Phase 2 — Vision pipeline (5)
7. `feat(backend): opencv webcam capture loop` — opens default camera, shows
   frames in a debug window, exits on `q`, logs FPS.
8. `feat(backend): integrate mediapipe HandLandmarker` — load task model, run per
   frame, keep landmarks in memory.
9. `feat(backend): draw landmarks + hand bbox in debug window` — overlay skeleton
   and bounding box on the cv2 preview.
10. `feat(backend): pick dominant hand + target landmark` — prefer "Right" if both
    present; select index fingertip (landmark 8) as the tracked point.
11. `feat(backend): landmark-stream callback interface` — decouple capture from
    analysis via a callback that accepts `(landmarks, frame_idx, timestamp)`.

### Phase 3 — Tremor analysis (5)
12. `feat(backend): TremorAnalyzer scaffold` — fixed-size rolling buffer of
    (timestamp, x, y, bbox_diag).
13. `feat(backend): detrending + RMS magnitude` — subtract moving-average baseline,
    compute RMS of residual.
14. `feat(backend): normalize magnitude by hand bbox diagonal` — produces
    scale-invariant tremor score.
15. `feat(backend): FFT dominant frequency in 3–15 Hz band` — use SciPy rfft, cap
    to band of interest.
16. `test(backend): TremorAnalyzer unit tests` — synthetic sine @ 6 Hz yields
    frequency ≈ 6 and non-zero magnitude; flat input yields ~0.

### Phase 4 — Backend service (4)
17. `feat(backend): FastAPI app + /health endpoint`.
18. `feat(backend): /ws/tremor websocket` — pushes `{level, magnitude, frequency,
    hand, timestamp}` at ~20 Hz from the analyzer.
19. `feat(backend): config via env vars` — `CAMERA_INDEX`, `TARGET_FPS`,
    `TREMOR_THRESHOLD`, `WS_RATE_HZ`.
20. `feat(backend): graceful shutdown` — release camera, cancel WS tasks on
    SIGINT/SIGTERM.

### Phase 5 — Frontend scaffolding (3)
21. `chore(frontend): Vite + React 18 + TS scaffold`.
22. `chore(frontend): Tailwind install + config + base styles`.
23. `chore(frontend): biome config + npm scripts`.

### Phase 6 — Frontend tremor plumbing (2)
24. `feat(frontend): useTremorSocket hook with reconnect` — opens WS, exposes last
    payload, reconnects with backoff on drop.
25. `feat(frontend): TremorContext + provider` — wraps `useTremorSocket`, exposes
    `{ level, magnitude, frequency, hand, connected }` to children.

### Phase 7 — Demo UI (5)
26. `feat(frontend): NumberPad baseline` — static, non-adaptive buttons + display
    buffer + clear. Establishes the "before" behavior.
27. `feat(frontend): AdaptiveButton — size scaling` — `min-height/width` scales
    1.0× → 1.8× with tremor level.
28. `feat(frontend): NumberPad — adaptive spacing` — gap scales 1.0× → 1.5×.
29. `feat(frontend): click debounce wired to level` — 0 ms @ level 0, 250 ms @
    level 1 via `useAdaptiveDebounce`.
30. `feat(frontend): EMA pointer smoothing utility + wire-up` — alpha scales with
    level; apply to drag/slider interactions in the demo.

### Phase 8 — Debug panel (3)
31. `feat(frontend): DebugPanel shell + connection status` — collapsible panel,
    shows WS state.
32. `feat(frontend): DebugPanel meter + frequency readouts` — live bar for
    `level`, numeric `magnitude` + `frequency`.
33. `feat(frontend): DebugPanel manual override slider` — slider forces `level`
    into the context for demoing without a real tremor.

### Phase 9 — Ship (2)
34. `docs: top-level README` — quick-start (backend venv + frontend npm),
    architecture diagram, known limitations.
35. `chore: tag v0.1.0-poc`.

(33 functional commits + initial = 32 numbered steps above; `v0.1.0-poc` tag closes
the PoC.)

## File Layout

```
CVUIA/
├── README.md
├── .gitignore
├── Makefile
├── PLAN.md / WIP.md / LEARNINGS.md
├── backend/
│   ├── pyproject.toml
│   ├── README.md
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI app + WS endpoint
│   │   ├── capture.py      # OpenCV + MediaPipe loop
│   │   ├── tremor.py       # TremorAnalyzer
│   │   ├── config.py       # env-var config
│   │   └── schema.py       # pydantic WS payload
│   └── tests/
│       ├── __init__.py
│       └── test_tremor.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── biome.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── context/TremorContext.tsx
        ├── hooks/
        │   ├── useTremorSocket.ts
        │   ├── useAdaptiveDebounce.ts
        │   └── useEmaSmoothing.ts
        └── components/
            ├── NumberPad.tsx
            ├── AdaptiveButton.tsx
            └── DebugPanel.tsx
```

## Risks / Open Questions
- **MediaPipe on Apple Silicon:** pip wheel parity has lagged historically. Fallback
  is `mediapipe-silicon` or Python 3.11 venv. Handled in step 4.
- **Latency budget:** OpenCV + MediaPipe + WS must stay under ~50 ms. If not, drop
  MediaPipe's internal smoothing and downsample frames.
- **Threshold is empirical:** the RMS value mapping to `level = 1` needs one tuning
  pass. Manual override (step 33) covers the demo path.
- **Auth for push:** pending — need `gh auth`, PAT, or SSH confirmed before step 1
  can push to origin.
