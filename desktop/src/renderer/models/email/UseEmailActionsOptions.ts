import type { MailProvider } from "../auth/MailProvider";

export interface UseEmailActionsOptions {
  provider: MailProvider;
  onEmailRemove: (emailId: string) => void;
  onPendingArchiveRemove: (emailId: string) => void;
  onEmailsReload: () => void;
}
