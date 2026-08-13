import type { ThemePreference } from "./ThemePreference";
import type { ResolvedTheme } from "./ResolvedTheme";

export interface UseThemeResult {
  themePreference: ThemePreference;
  theme: ResolvedTheme;
  cycleTheme: () => void;
}
