import type { Email } from "../../types";

export interface EmailCardProps {
  email: Email;
  onClick: () => void;
  onArchive?: () => void;
}