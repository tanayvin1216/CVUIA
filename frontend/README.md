# frontend

React + Vite + TypeScript + Tailwind. Connects to the backend WebSocket and
renders a number-pad demo whose buttons scale, space out, smooth input, and
debounce clicks based on live tremor metrics.

Structure (populated over the next commits):

```
src/
  main.tsx
  App.tsx
  context/TremorContext.tsx
  hooks/
    useTremorSocket.ts
    useAdaptiveDebounce.ts
    useEmaSmoothing.ts
  components/
    NumberPad.tsx
    AdaptiveButton.tsx
    DebugPanel.tsx
```

Run instructions land at step 34 when the top-level README is finalized.
