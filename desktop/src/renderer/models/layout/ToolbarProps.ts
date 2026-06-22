export interface ToolbarProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
}
