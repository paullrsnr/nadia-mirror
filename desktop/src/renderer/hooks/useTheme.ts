import { useContext } from "react";
import { ThemeContext } from "../context/ThemeContext";
import type { ThemeContextValue } from "../context/ThemeContext";

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used inside ThemeProvider");
  return ctx;
}
