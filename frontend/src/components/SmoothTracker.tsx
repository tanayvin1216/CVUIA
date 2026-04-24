import { useRef, useState } from "react";

import { useTremor } from "@/context/TremorContext";
import { useEmaPoint } from "@/hooks/useEmaSmoothing";

const MIN_ALPHA = 0.25; // at level 1 — heavy smoothing
const MAX_ALPHA = 1.0; // at level 0 — pass-through

export function SmoothTracker() {
  const { level } = useTremor();
  const alpha = MAX_ALPHA - (MAX_ALPHA - MIN_ALPHA) * level;
  const padRef = useRef<HTMLDivElement>(null);
  const [raw, setRaw] = useState({ x: 0.5, y: 0.5 });
  const smoothed = useEmaPoint(raw, alpha);

  const onPointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!padRef.current) return;
    const rect = padRef.current.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width;
    const y = (event.clientY - rect.top) / rect.height;
    setRaw({ x: clamp01(x), y: clamp01(y) });
  };

  return (
    <div className="flex flex-col gap-3">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-calm">
        pointer smoothing demo
      </p>
      <div
        ref={padRef}
        onPointerMove={onPointerMove}
        className="relative h-56 w-full rounded-sm border border-ink/20 bg-ink/[0.03] touch-none"
      >
        <Marker x={raw.x} y={raw.y} tone="raw" label="raw" />
        <Marker x={smoothed.x} y={smoothed.y} tone="smoothed" label="smooth" />
      </div>
      <div className="flex items-center justify-between font-mono text-xs text-calm">
        <span>alpha · {alpha.toFixed(2)}</span>
        <span className="text-ink/40">hover the pad</span>
      </div>
    </div>
  );
}

function Marker({
  x,
  y,
  tone,
  label,
}: {
  x: number;
  y: number;
  tone: "raw" | "smoothed";
  label: string;
}) {
  const color =
    tone === "raw"
      ? "border-ink/30 bg-paper text-ink/50"
      : "border-accent bg-accent/90 text-paper";
  return (
    <div
      className={`pointer-events-none absolute flex h-6 w-6 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border font-mono text-[9px] uppercase tracking-wide ${color}`}
      style={{ left: `${x * 100}%`, top: `${y * 100}%` }}
    >
      {label[0]}
    </div>
  );
}

function clamp01(n: number): number {
  return Math.max(0, Math.min(1, n));
}
