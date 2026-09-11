import "./ComposeActionButton.css";
import Button from "../../ui/Button";
import { IconCompose, IconSend } from "../../ui/icons";
import { COMPOSE_ACTION_LABELS } from "../../../constants/labels";
import type { ComposeActionButtonProps } from "../../../models";

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
      {COMPOSE_ACTION_LABELS[mode]}
    </Button>
  );
}
