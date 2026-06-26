import "./ComposeActionButton.css";
import Button from "../ui/Button";
import { IconCompose, IconSend } from "../ui/icons";
import type { ComposeActionButtonProps } from "../../models";

const LABELS = {
  new: "Nouveau message",
  send: "Envoyer",
} as const;

export default function ComposeActionButton({ mode, onClick, disabled, className }: ComposeActionButtonProps) {
  const Icon = mode === "new" ? IconCompose : IconSend;
  return (
    <Button
      variant="primary"
      disabled={disabled}
      onClick={onClick}
      className={`compose-action-btn ${className ?? ""}`.trim()}
    >
      <Icon />
      {LABELS[mode]}
    </Button>
  );
}
