export interface ComposeToolbarProps {
  execFormat: (command: string, value?: string) => void;
  resetTextColor: () => void;
  toggleHighlight: (color: string) => void;
  resetHighlight: () => void;
}
