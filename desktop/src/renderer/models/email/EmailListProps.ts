import type { Email } from "./Email";
import type { Category } from "./Category";
import type { MailProvider } from "../auth/MailProvider";

export interface EmailListProps {
  emails: Email[];
  pendingArchive: Email[];
  categories: Category[];
  loading: boolean;
  syncing: boolean;
  classifying: boolean;
  error: string | null;
  provider: MailProvider;
  categoryFilter: string;
  onProviderChange: (p: MailProvider) => void;
  onCategoryFilterChange: (cat: string) => void;
  onSync: (full: boolean) => void;
  onClassifyAll: () => void;
  onEmailClick: (email: Email) => void;
  onArchive: (email: Email) => void;
  onConfirmArchive: (email: Email) => void;
  onRejectArchive: (email: Email) => void;
}
