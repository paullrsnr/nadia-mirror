import type { Email, Category } from ".";

export interface UseEmailsResult {
  emails: Email[];
  pendingArchive: Email[];
  categories: Category[];
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  loadEmails: () => Promise<void>;
  loadAll: () => Promise<void>;
  removeEmail: (emailId: string) => void;
  removePendingArchive: (emailId: string) => void;
}
