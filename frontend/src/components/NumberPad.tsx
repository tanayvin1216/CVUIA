import { useCallback, useState } from "react";

const MAX_LENGTH = 12;

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

  const press = useCallback((key: Key) => {
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

  return (
    <div className="flex w-full max-w-md flex-col gap-6">
      <div
        aria-live="polite"
        className="flex min-h-[4.5rem] items-end justify-end border-b border-ink/20 pb-3 font-mono text-4xl tabular-nums tracking-tight text-ink"
      >
        {buffer || <span className="text-ink/30">—</span>}
      </div>

      <div className="grid grid-cols-3 gap-3">
        {KEYS.map((key, idx) => (
          <PadButton
            key={keyId(key, idx)}
            onClick={() => press(key)}
            label={labelFor(key)}
            variant={key.kind === "digit" || key.kind === "dot" ? "primary" : "muted"}
          />
        ))}
        <PadButton
          onClick={() => press({ kind: "clear" })}
          label="Clear"
          variant="accent"
          className="col-span-3"
        />
      </div>
    </div>
  );
}

interface PadButtonProps {
  label: string;
  onClick: () => void;
  variant: "primary" | "muted" | "accent";
  className?: string;
}

function PadButton({ label, onClick, variant, className }: PadButtonProps) {
  const base =
    "flex items-center justify-center rounded-md border font-mono text-2xl tabular-nums transition-colors duration-100 select-none";
  const variants = {
    primary: "border-ink/15 bg-paper text-ink hover:bg-ink/5 active:bg-ink/10",
    muted: "border-ink/10 bg-ink/5 text-ink/70 hover:bg-ink/10 active:bg-ink/15",
    accent: "border-accent/30 bg-accent/10 text-accent hover:bg-accent/20 active:bg-accent/25",
  } as const;
  const size = "min-h-[4.5rem]";
  return (
    <button
      type="button"
      onClick={onClick}
      className={`${base} ${variants[variant]} ${size} ${className ?? ""}`.trim()}
    >
      {label}
    </button>
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
