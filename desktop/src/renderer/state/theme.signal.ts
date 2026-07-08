import { signal, computed, effect } from "@preact/signals-react";
import type { ThemePreference, ResolvedTheme } from "../models/theme";
import {
  THEME_STORAGE_KEY,
  THEME_CYCLE,
  THEME_LIGHT,
  THEME_DARK,
  THEME_SYSTEM,
} from "../constants/theme";

const DARK_MEDIA_QUERY = "(prefers-color-scheme: dark)";

function readStoredPreference(): ThemePreference {
  const stored = localStorage.getItem(THEME_STORAGE_KEY) as ThemePreference | null;
  return stored && THEME_CYCLE.includes(stored) ? stored : THEME_SYSTEM;
}

function getSystemTheme(): ResolvedTheme {
  return window.matchMedia(DARK_MEDIA_QUERY).matches ? THEME_DARK : THEME_LIGHT;
}

export const themePreferenceSignal = signal<ThemePreference>(readStoredPreference());

const systemThemeSignal = signal<ResolvedTheme>(getSystemTheme());

window.matchMedia(DARK_MEDIA_QUERY).addEventListener("change", (e) => {
  systemThemeSignal.value = e.matches ? THEME_DARK : THEME_LIGHT;
});

export const resolvedTheme = computed<ResolvedTheme>(() =>
  themePreferenceSignal.value === THEME_SYSTEM ? systemThemeSignal.value : themePreferenceSignal.value,
);

export function cycleTheme(): void {
  const current = themePreferenceSignal.value;
  themePreferenceSignal.value = THEME_CYCLE[(THEME_CYCLE.indexOf(current) + 1) % THEME_CYCLE.length];
}

effect(() => {
  localStorage.setItem(THEME_STORAGE_KEY, themePreferenceSignal.value);
});

effect(() => {
  document.documentElement.setAttribute("data-theme", resolvedTheme.value);
});
