# Learnings

Running log of decisions, surprises, and things to remember. Append-only.

## 2026-04-23 — initial planning
- **Stack split is intentional.** User asked for Python MediaPipe + diverse-but-not-
  too-diverse tech. Chose Python (CV/analysis) + React (adaptive UI) + WebSocket
  bridge. Avoided a single-language solution (pure web MediaPipe) because the user
  specifically wanted Python in the loop.
- **MediaPipe Tasks API over the legacy Solutions API.** `HandLandmarker` from
  `mediapipe.tasks.python.vision` is the current supported path; `mp.solutions.hands`
  is legacy.
- **Tremor detection approach.** Essential tremor sits in the 4–12 Hz band;
  Parkinsonian resting tremor is 3–6 Hz. A rolling RMS after detrending is a cheap,
  robust proxy for "how shaky is the hand right now" — good enough for a PoC without
  needing classification. FFT adds frequency as a secondary signal.
- **Normalization matters.** Pixel-space magnitude depends on distance to camera.
  Divide by hand bounding-box diagonal so the metric is scale-invariant.
- **Adaptation channels.** Three orthogonal adaptations: (1) target size, (2)
  spacing, (3) input temporal filtering (smoothing + debounce). All driven by one
  `level ∈ [0,1]` scalar — keeps the product surface small.
- **Manual override is non-optional.** Demoing tremor adaptation without actually
  having a tremor requires a slider. Built into the debug panel from the start.

## Open questions to resolve during build
- Does the Mac webcam give consistent 30 fps under MediaPipe load? If not, we adapt
  the buffer window (seconds, not frames).
- Is `mediapipe` installable cleanly via pip on the target machine? Fallback plan is
  in PLAN.md step 2.
