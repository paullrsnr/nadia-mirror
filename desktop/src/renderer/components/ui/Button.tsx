import React from "react";
import { colors, spacing, radius, typography } from "../../styles";
import type { ButtonProps, ButtonVariant, ButtonSize } from "../../types";

const variantStyles: Record<ButtonVariant, React.CSSProperties> = {
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
  tertiary: {
    backgroundColor: "transparent",
    color: colors.textSecondary,
    border: `1px solid ${colors.borderStrong}`,
  },
};

const sizeStyles: Record<ButtonSize, React.CSSProperties> = {
  sm: { padding: `${spacing.xs} ${spacing.md}`, fontSize: typography.fontSizeSm },
  md: { padding: `${spacing.sm} 16px`, fontSize: typography.fontSizeBase },
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
