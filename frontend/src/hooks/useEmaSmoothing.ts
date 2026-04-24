import { useEffect, useRef, useState } from "react";

/**
 * Exponential moving average of a 2D point, with alpha scaled externally by
 * tremor level:  out = alpha·raw + (1-alpha)·out_prev.
 *
 *   alpha = 1.0 → pass-through (no smoothing)
 *   alpha = 0.1 → very heavy smoothing
 *
 * The smoothed value updates on every `raw` change.
 */
export function useEmaPoint(raw: { x: number; y: number }, alpha: number): {
  x: number;
  y: number;
} {
  const [smoothed, setSmoothed] = useState(raw);
  const ref = useRef(smoothed);

  useEffect(() => {
    const a = Math.max(0, Math.min(1, alpha));
    const prev = ref.current;
    const next = {
      x: a * raw.x + (1 - a) * prev.x,
      y: a * raw.y + (1 - a) * prev.y,
    };
    ref.current = next;
    setSmoothed(next);
  }, [raw, alpha]);

  return smoothed;
}
