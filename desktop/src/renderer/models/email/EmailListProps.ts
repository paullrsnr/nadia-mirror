import type { Email } from "./Email";
import type { InboxFolder } from "./InboxFolder";
import type { MailProvider } from "../auth/MailProvider";

export interface EmailListProps {
  emails: Email[];
  pendingArchive: Email[];
  loading: boolean;
  syncing: boolean;
  classifying: boolean;
  error: string | null;
  provider: MailProvider;
  folder: InboxFolder;
  categoryFilter: string;
  searchValue: string;
  selectedEmailId: string | null;
  onSync: (full: boolean) => void;
  onClassifyAll: () => void;
  onEmailClick: (email: Email) => void;
  onArchive: (email: Email) => void;
  onToggleStar: (email: Email) => void;
  onConfirmArchive: (email: Email) => void;
  onRejectArchive: (email: Email) => void;
}
