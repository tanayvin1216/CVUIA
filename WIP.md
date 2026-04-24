# WIP

Current step: **0 — awaiting plan approval**

## Progress (32 atomic commits, each pushed individually)

### Phase 0 — Repo bootstrap
- [ ] 1. chore: initial commit (.gitignore, README stub, planning docs) + push
- [ ] 2. chore: add backend/ directory skeleton
- [ ] 3. chore: add frontend/ directory skeleton

### Phase 1 — Backend scaffolding
- [ ] 4. chore(backend): pyproject.toml with pinned deps
- [ ] 5. chore(backend): ruff + pytest config
- [ ] 6. chore: root Makefile

### Phase 2 — Vision pipeline
- [ ] 7. feat(backend): OpenCV webcam capture loop
- [ ] 8. feat(backend): integrate MediaPipe HandLandmarker
- [ ] 9. feat(backend): draw landmarks + bbox in debug window
- [ ] 10. feat(backend): pick dominant hand + target landmark
- [ ] 11. feat(backend): landmark-stream callback interface

### Phase 3 — Tremor analysis
- [ ] 12. feat(backend): TremorAnalyzer scaffold (rolling buffer)
- [ ] 13. feat(backend): detrending + RMS magnitude
- [ ] 14. feat(backend): normalize magnitude by hand bbox diagonal
- [ ] 15. feat(backend): FFT dominant frequency in 3–15 Hz band
- [ ] 16. test(backend): TremorAnalyzer unit tests

### Phase 4 — Backend service
- [ ] 17. feat(backend): FastAPI app + /health endpoint
- [ ] 18. feat(backend): /ws/tremor WebSocket endpoint
- [ ] 19. feat(backend): config via env vars
- [ ] 20. feat(backend): graceful shutdown

### Phase 5 — Frontend scaffolding
- [ ] 21. chore(frontend): Vite + React 18 + TS scaffold
- [ ] 22. chore(frontend): Tailwind + base styles
- [ ] 23. chore(frontend): biome config + npm scripts

### Phase 6 — Frontend tremor plumbing
- [ ] 24. feat(frontend): useTremorSocket hook with reconnect
- [ ] 25. feat(frontend): TremorContext + provider

### Phase 7 — Demo UI
- [ ] 26. feat(frontend): NumberPad baseline
- [ ] 27. feat(frontend): AdaptiveButton — size scaling
- [ ] 28. feat(frontend): NumberPad — adaptive spacing
- [ ] 29. feat(frontend): click debounce wired to level
- [ ] 30. feat(frontend): EMA pointer smoothing utility + wire-up

### Phase 8 — Debug panel
- [ ] 31. feat(frontend): DebugPanel shell + connection status
- [ ] 32. feat(frontend): DebugPanel meter + frequency readouts
- [ ] 33. feat(frontend): DebugPanel manual override slider

### Phase 9 — Ship
- [ ] 34. docs: top-level README (quick-start, architecture, limitations)
- [ ] 35. chore: tag v0.1.0-poc

## Notes for the next turn
- Remote: `https://github.com/tanayvin1216/CVUIA.git` — user confirmed.
- Commit per step, push after each. Conventional Commits. No AI co-author.
- Need git auth confirmed before step 1's push (gh auth, PAT, or SSH).
