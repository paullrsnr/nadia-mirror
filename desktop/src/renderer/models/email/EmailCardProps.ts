import type { Email } from "./Email";

export interface EmailCardProps {
  email: Email;
  isSelected?: boolean;
  onClick: () => void;
  onArchive?: () => void;
  onToggleStar?: () => void;
}