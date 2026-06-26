import type { DraftEmail } from "./DraftEmail";

export interface UseDraftsResult {
  drafts: DraftEmail[];
  loading: boolean;
  error: string | null;
  loadDrafts: () => Promise<void>;
  removeDraft: (draftId: string) => void;
}
