import type { MailProvider } from "../auth/MailProvider";
import type { ComposeMode } from "./ComposeState";
import type { DraftEmail } from "./DraftEmail";
import type { Email } from "./Email";

export interface UseComposeDraftOptions {
  provider: MailProvider;
  mode: ComposeMode;
  replyTo?: Email;
  existingDraft?: DraftEmail;
  onSent: (draftId: string, subject: string) => void;
}
