import { useComputed } from "@preact/signals-react";
import { themePreferenceSignal, resolvedTheme, cycleTheme } from "../state";
import type { UseThemeResult } from "../models/theme";

export function useTheme(): UseThemeResult {
  const themePreference = useComputed(() => themePreferenceSignal.value).value;
  const theme = useComputed(() => resolvedTheme.value).value;
  return { themePreference, theme, cycleTheme };
}
