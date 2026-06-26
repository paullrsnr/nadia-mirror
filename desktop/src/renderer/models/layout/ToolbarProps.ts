import type { ThemePreference } from "../theme";

export interface ToolbarProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  themePreference: ThemePreference;
  onCycleTheme: () => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  onComposeClick: () => void;
}
