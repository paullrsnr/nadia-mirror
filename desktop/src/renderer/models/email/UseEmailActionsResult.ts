import type { Email } from ".";

export interface UseEmailActionsResult {
  classifying: boolean;
  summarizing: boolean;
  drafting: boolean;
  summary: string | null;
  draft: string | null;
  threadCount: number;
  actionError: string | null;
  resetDetail: () => void;
  loadThread: (email: Email) => Promise<void>;
  handleClassify: (email: Email) => Promise<void>;
  handleClassifyAll: () => Promise<void>;
  handleSummarize: (email: Email) => Promise<void>;
  handleSummarizeThread: (email: Email) => Promise<void>;
  handleSuggestReply: (email: Email) => Promise<void>;
  handleArchive: (email: Email) => Promise<void>;
  handleConfirmArchive: (email: Email) => Promise<void>;
  handleRejectArchive: (email: Email) => Promise<void>;
}
