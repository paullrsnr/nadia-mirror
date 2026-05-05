import React from "react";
import { colors, spacing, radius } from "../../theme";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantStyles: Record<Variant, React.CSSProperties> = {
  primary: {
    backgroundColor: colors.buttonPrimary,
    color: colors.background,
    border: "none",
  },
  secondary: {
    backgroundColor: colors.backgroundMuted,
    color: colors.textSecondary,
    border: `1px solid ${colors.borderStrong}`,
  },
  ghost: {
    backgroundColor: "transparent",
    color: colors.textSecondary,
    border: `1px solid ${colors.borderStrong}`,
  },
};

const sizeStyles: Record<Size, React.CSSProperties> = {
  sm: { padding: "4px 10px", fontSize: "12px" },
  md: { padding: `${spacing.sm}px 16px`, fontSize: "14px" },
};

export default function Button({
  variant = "primary",
  size = "md",
  disabled,
  style,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled}
      style={{
        borderRadius: radius.sm,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.65 : 1,
        ...variantStyles[variant],
        ...sizeStyles[size],
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  );
}
