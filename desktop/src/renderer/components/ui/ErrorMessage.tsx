import React from "react";
import { colors, spacing, radius } from "../../theme";

interface ErrorMessageProps {
  message: string;
  style?: React.CSSProperties;
}

export default function ErrorMessage({ message, style }: ErrorMessageProps) {
  return (
    <div
      role="alert"
      style={{
        padding: spacing.card,
        backgroundColor: "#ffebee",
        color: colors.error,
        borderRadius: radius.sm,
        fontSize: "13px",
        ...style,
      }}
    >
      {message}
    </div>
  );
}
