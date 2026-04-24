import { useCallback, useRef } from "react";

import { useTremor } from "@/context/TremorContext";

const MAX_DEBOUNCE_MS = 250;

/**
 * Wraps `fn` in a leading-edge debouncer whose window scales with tremor level:
 * 0 ms at level 0 (pass-through), MAX_DEBOUNCE_MS at level 1. The first call in
 * each window fires immediately; repeats inside the window are dropped. This
 * collapses the common failure mode where a shaky tap double-registers.
 */
export function useAdaptiveDebounce<T extends unknown[]>(
  fn: (...args: T) => void,
): (...args: T) => void {
  const { level } = useTremor();
  const lastCallRef = useRef(0);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  return useCallback(
    (...args: T) => {
      const windowMs = level * MAX_DEBOUNCE_MS;
      const now = performance.now();
      if (windowMs > 0 && now - lastCallRef.current < windowMs) return;
      lastCallRef.current = now;
      fnRef.current(...args);
    },
    [level],
  );
}
