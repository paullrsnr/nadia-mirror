import type { DraftEmail } from "./DraftEmail";

export interface DraftCardProps {
  draft: DraftEmail;
  onClick: () => void;
  onDelete: () => void;
}
