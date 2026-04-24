import { useCallback, useState } from "react";

import { AdaptiveButton } from "@/components/AdaptiveButton";
import { useTremor } from "@/context/TremorContext";
import { useAdaptiveDebounce } from "@/hooks/useAdaptiveDebounce";

const MAX_LENGTH = 12;
const BASE_GAP_REM = 0.75; // corresponds to gap-3
const MAX_GAP_MULTIPLIER = 1.5;

type Key =
  | { kind: "digit"; value: string }
  | { kind: "dot" }
  | { kind: "back" }
  | { kind: "clear" };

const KEYS: Key[] = [
  { kind: "digit", value: "1" },
  { kind: "digit", value: "2" },
  { kind: "digit", value: "3" },
  { kind: "digit", value: "4" },
  { kind: "digit", value: "5" },
  { kind: "digit", value: "6" },
  { kind: "digit", value: "7" },
  { kind: "digit", value: "8" },
  { kind: "digit", value: "9" },
  { kind: "dot" },
  { kind: "digit", value: "0" },
  { kind: "back" },
];

export function NumberPad() {
  const [buffer, setBuffer] = useState("");
  const { level } = useTremor();
  const gapRem = BASE_GAP_REM * (1 + (MAX_GAP_MULTIPLIER - 1) * level);

  const rawPress = useCallback((key: Key) => {
    setBuffer((prev) => {
      if (key.kind === "clear") return "";
      if (key.kind === "back") return prev.slice(0, -1);
      if (key.kind === "dot") {
        if (prev.includes(".")) return prev;
        return prev.length < MAX_LENGTH ? (prev === "" ? "0." : prev + ".") : prev;
      }
      return prev.length < MAX_LENGTH ? prev + key.value : prev;
    });
  }, []);
  const press = useAdaptiveDebounce(rawPress);

  return (
    <div className="flex w-full max-w-md flex-col gap-6">
      <div
        aria-live="polite"
        className="flex min-h-[4.5rem] items-end justify-end border-b border-ink/20 pb-3 font-mono text-4xl tabular-nums tracking-tight text-ink"
      >
        {buffer || <span className="text-ink/30">—</span>}
      </div>

      <div
        className="grid grid-cols-3 transition-[gap] duration-200 ease-out"
        style={{ gap: `${gapRem}rem` }}
      >
        {KEYS.map((key, idx) => (
          <AdaptiveButton
            key={keyId(key, idx)}
            onClick={() => press(key)}
            variant={key.kind === "digit" || key.kind === "dot" ? "primary" : "muted"}
          >
            {labelFor(key)}
          </AdaptiveButton>
        ))}
        <AdaptiveButton
          onClick={() => press({ kind: "clear" })}
          variant="accent"
          className="col-span-3"
        >
          Clear
        </AdaptiveButton>
      </div>
    </div>
  );
}

function keyId(key: Key, idx: number): string {
  if (key.kind === "digit") return `d-${key.value}`;
  return `${key.kind}-${idx}`;
}

function labelFor(key: Key): string {
  switch (key.kind) {
    case "digit":
      return key.value;
    case "dot":
      return ".";
    case "back":
      return "⌫";
    case "clear":
      return "Clear";
  }
}
