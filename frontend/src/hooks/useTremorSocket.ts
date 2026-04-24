import { useEffect, useRef, useState } from "react";

import type { TremorPayload } from "@/types/tremor";

const BACKOFF_SCHEDULE_MS = [500, 1000, 2000, 4000, 5000] as const;

export interface UseTremorSocketResult {
  payload: TremorPayload | null;
  connected: boolean;
}

export function useTremorSocket(url: string): UseTremorSocketResult {
  const [payload, setPayload] = useState<TremorPayload | null>(null);
  const [connected, setConnected] = useState(false);
  const attemptRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const cancelledRef = useRef(false);

  useEffect(() => {
    cancelledRef.current = false;

    const connect = () => {
      if (cancelledRef.current) return;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.addEventListener("open", () => {
        if (cancelledRef.current) {
          ws.close();
          return;
        }
        attemptRef.current = 0;
        setConnected(true);
      });

      ws.addEventListener("message", (event) => {
        try {
          const parsed = JSON.parse(event.data) as TremorPayload;
          setPayload(parsed);
        } catch (err) {
          console.warn("useTremorSocket: malformed payload", err);
        }
      });

      ws.addEventListener("close", () => {
        setConnected(false);
        if (cancelledRef.current) return;
        const delay =
          BACKOFF_SCHEDULE_MS[
            Math.min(attemptRef.current, BACKOFF_SCHEDULE_MS.length - 1)
          ] ?? 5000;
        attemptRef.current += 1;
        timerRef.current = setTimeout(connect, delay);
      });

      ws.addEventListener("error", () => {
        // Errors are surfaced via the subsequent close event.
      });
    };

    connect();

    return () => {
      cancelledRef.current = true;
      if (timerRef.current) clearTimeout(timerRef.current);
      if (wsRef.current && wsRef.current.readyState <= WebSocket.OPEN) {
        wsRef.current.close();
      }
      wsRef.current = null;
      setConnected(false);
    };
  }, [url]);

  return { payload, connected };
}
