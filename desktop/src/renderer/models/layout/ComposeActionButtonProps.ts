export type ComposeActionMode = "new" | "send";

export interface ComposeActionButtonProps {
  mode: ComposeActionMode;
  onClick: () => void;
  disabled?: boolean;
  className?: string;
}
