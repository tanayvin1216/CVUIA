import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { useTremorSocket } from "@/hooks/useTremorSocket";
import { ZERO_PAYLOAD, type Handedness, type TremorPayload } from "@/types/tremor";

const DEFAULT_WS_URL =
  import.meta.env.VITE_TREMOR_WS_URL ?? "ws://127.0.0.1:8000/ws/tremor";

export interface TremorState {
  /** Current effective tremor level, clamped [0, 1]. Override wins over live payload. */
  level: number;
  magnitude: number;
  frequency: number;
  hand: Handedness;
  samples: number;
  timestamp: number;
  connected: boolean;
  /** Raw live payload from the WS, ignoring the override. Useful for debug readouts. */
  livePayload: TremorPayload;
  /** If non-null, this value is used as `level` instead of the live payload. */
  override: number | null;
  setOverride: (value: number | null) => void;
}

const TremorContext = createContext<TremorState | null>(null);

interface TremorProviderProps {
  children: ReactNode;
  wsUrl?: string;
}

export function TremorProvider({ children, wsUrl = DEFAULT_WS_URL }: TremorProviderProps) {
  const { payload, connected } = useTremorSocket(wsUrl);
  const [override, setOverride] = useState<number | null>(null);

  const handleSetOverride = useCallback((value: number | null) => {
    if (value === null) {
      setOverride(null);
      return;
    }
    const clamped = Math.max(0, Math.min(1, value));
    setOverride(clamped);
  }, []);

  const value = useMemo<TremorState>(() => {
    const live = payload ?? ZERO_PAYLOAD;
    const effectiveLevel = override ?? live.level;
    return {
      level: effectiveLevel,
      magnitude: live.magnitude,
      frequency: live.frequency,
      hand: live.hand,
      samples: live.samples,
      timestamp: live.timestamp,
      connected,
      livePayload: live,
      override,
      setOverride: handleSetOverride,
    };
  }, [payload, connected, override, handleSetOverride]);

  return <TremorContext.Provider value={value}>{children}</TremorContext.Provider>;
}

export function useTremor(): TremorState {
  const ctx = useContext(TremorContext);
  if (!ctx) throw new Error("useTremor must be used inside <TremorProvider>");
  return ctx;
}
