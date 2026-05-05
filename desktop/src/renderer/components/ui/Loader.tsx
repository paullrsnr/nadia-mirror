import React from "react";
import { colors } from "../../theme";

interface LoaderProps {
  size?: number;
  label?: string;
  fullPage?: boolean;
}

const spinStyle: React.CSSProperties = {
  display: "inline-block",
  borderRadius: "50%",
  borderStyle: "solid",
  borderColor: colors.border,
  animation: "spin 1s linear infinite",
};

export default function Loader({ size = 32, label, fullPage = false }: LoaderProps) {
  const spinner = (
    <div
      style={{
        ...spinStyle,
        width: size,
        height: size,
        borderWidth: size >= 48 ? 4 : 3,
        borderTopColor: colors.buttonPrimary,
      }}
      role="status"
      aria-label={label ?? "Chargement..."}
    />
  );

  if (fullPage) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "60vh",
          gap: 16,
        }}
      >
        {spinner}
        {label && <p style={{ color: colors.textMuted, margin: 0 }}>{label}</p>}
      </div>
    );
  }

  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
      {spinner}
      {label && <span style={{ color: colors.textMuted }}>{label}</span>}
    </div>
  );
}
