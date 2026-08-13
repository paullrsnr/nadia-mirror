import type { ThemePreference, ResolvedTheme } from "../models/theme";
import { IconSun, IconMoon, IconThemeSystem } from "../components/ui/icons";

export const THEME_STORAGE_KEY = "nadia-theme";

export const THEME_LIGHT = "light" satisfies ResolvedTheme;
export const THEME_DARK = "dark" satisfies ResolvedTheme;
export const THEME_SYSTEM = "system" satisfies ThemePreference;

export const THEME_ICON: Record<ThemePreference, typeof IconSun> = {
  [THEME_LIGHT]: IconSun,
  [THEME_DARK]: IconMoon,
  [THEME_SYSTEM]: IconThemeSystem,
};

export const THEME_LABEL: Record<ThemePreference, string> = {
  [THEME_LIGHT]: "Clair",
  [THEME_DARK]: "Sombre",
  [THEME_SYSTEM]: "Système",
};

export const THEME_CYCLE = Object.keys(THEME_LABEL) as ThemePreference[];
