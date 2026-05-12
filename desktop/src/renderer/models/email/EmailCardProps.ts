import type { Email } from "./Email";

export interface EmailCardProps {
  email: Email;
  onClick: () => void;
  onArchive?: () => void;
}