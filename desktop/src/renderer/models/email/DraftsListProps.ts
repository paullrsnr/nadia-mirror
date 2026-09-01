import type { DraftEmail } from "./DraftEmail";

export interface DraftsListProps {
  drafts: DraftEmail[];
  loading: boolean;
  error: string | null;
  onDraftClick: (draft: DraftEmail) => void;
  onDraftDelete: (draft: DraftEmail) => void;
}
