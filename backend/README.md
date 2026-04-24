# backend

Python service: webcam capture, MediaPipe hand tracking, tremor analysis,
WebSocket stream.

Structure (populated over the next commits):

```
app/
  main.py     # FastAPI app + /ws/tremor endpoint
  capture.py  # OpenCV + MediaPipe loop
  tremor.py   # TremorAnalyzer (rolling buffer, RMS, FFT)
  config.py   # env-var config
  schema.py   # pydantic WS payloads
tests/
  test_tremor.py
```

Run instructions land at step 34 when the top-level README is finalized.
