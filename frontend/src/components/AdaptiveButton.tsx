import { forwardRef, type ButtonHTMLAttributes, type CSSProperties } from "react";

import { useTremor } from "@/context/TremorContext";

export type AdaptiveButtonVariant = "primary" | "muted" | "accent";

export interface AdaptiveButtonProps
  extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "type"> {
  variant?: AdaptiveButtonVariant;
  /** Base min-height in rems when tremor level is 0. Scales up to 1.8x at level 1. */
  baseHeightRem?: number;
  /** Base font-size in rems. Scales with sqrt(scale) so typography stays proportional. */
  baseFontRem?: number;
}

const VARIANTS: Record<AdaptiveButtonVariant, string> = {
  primary: "border-ink/15 bg-paper text-ink hover:bg-ink/5 active:bg-ink/10",
  muted: "border-ink/10 bg-ink/5 text-ink/70 hover:bg-ink/10 active:bg-ink/15",
  accent: "border-accent/30 bg-accent/10 text-accent hover:bg-accent/20 active:bg-accent/25",
};

const BASE_CLASSES =
  "flex items-center justify-center rounded-md border font-mono tabular-nums select-none " +
  "transition-[min-height,font-size] duration-200 ease-out " +
  "disabled:cursor-not-allowed disabled:opacity-50";

export const AdaptiveButton = forwardRef<HTMLButtonElement, AdaptiveButtonProps>(
  function AdaptiveButton(
    {
      variant = "primary",
      baseHeightRem = 4.5,
      baseFontRem = 1.5,
      className,
      style,
      children,
      ...rest
    },
    ref,
  ) {
    const { level } = useTremor();
    const scale = 1 + 0.8 * level; // 1.0x → 1.8x
    const dynamicStyle: CSSProperties = {
      minHeight: `${baseHeightRem * scale}rem`,
      fontSize: `${baseFontRem * Math.sqrt(scale)}rem`,
      ...style,
    };
    return (
      <button
        ref={ref}
        type="button"
        style={dynamicStyle}
        className={[BASE_CLASSES, VARIANTS[variant], className ?? ""].join(" ").trim()}
        {...rest}
      >
        {children}
      </button>
    );
  },
);
