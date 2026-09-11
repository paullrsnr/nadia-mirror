import type { ConnectableProvider } from "../auth/ConnectableProvider";
import type { ComposeMode } from "./ComposeState";
import type { DraftEmail } from "./DraftEmail";
import type { Email } from "./Email";

export interface ComposeModalProps {
  provider: ConnectableProvider;
  mode: ComposeMode;
  replyTo?: Email;
  existingDraft?: DraftEmail;
  onClose: () => void;
  onSendRequested: (draftId: string, subject: string) => void;
}
