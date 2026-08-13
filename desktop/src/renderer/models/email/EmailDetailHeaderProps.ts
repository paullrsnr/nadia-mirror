import type { Email } from "./Email";

export interface EmailDetailHeaderProps {
  email: Email;
  threadCount: number;
  classifying: boolean;
  summarizing: boolean;
  drafting: boolean;
  nadiaOpen: boolean;
  onToggleNadia: () => void;
  onClassify: (email: Email) => void;
  onSummarize: (email: Email) => void;
  onSummarizeThread: (email: Email) => void;
  onSuggestReply: (email: Email) => void;
  onToggleStar: (email: Email) => void;
}
