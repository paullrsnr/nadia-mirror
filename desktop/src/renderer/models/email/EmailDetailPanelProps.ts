import type { Email } from "./Email";

export interface EmailDetailPanelProps {
  email: Email | null;
  summary: string | null;
  draft: string | null;
  threadCount: number;
  classifying: boolean;
  summarizing: boolean;
  drafting: boolean;
  onClassify: (email: Email) => void;
  onSummarize: (email: Email) => void;
  onSummarizeThread: (email: Email) => void;
  onSuggestReply: (email: Email) => void;
  onToggleStar: (email: Email) => void;
  onReply: (email: Email) => void;
  onForward: (email: Email) => void;
}
