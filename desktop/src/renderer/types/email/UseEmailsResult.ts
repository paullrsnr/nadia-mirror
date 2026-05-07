import type { Email, Category } from ".";

export interface UseEmailsResult {
  emails: Email[];
  pendingArchive: Email[];
  categories: Category[];
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  loadEmails: () => Promise<void>;
  loadPendingArchive: () => Promise<void>;
  updateEmail: (emailId: string, patch: Partial<Email>) => void;
  removeEmail: (emailId: string) => void;
  removePendingArchive: (emailId: string) => void;
}
