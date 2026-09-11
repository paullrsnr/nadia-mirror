import type { ConnectableProvider } from "../auth/ConnectableProvider";
import type { ComposeMode } from "./ComposeState";
import type { DraftEmail } from "./DraftEmail";
import type { Email } from "./Email";

export interface UseComposeDraftOptions {
  provider: ConnectableProvider;
  mode: ComposeMode;
  replyTo?: Email;
  existingDraft?: DraftEmail;
  onSent: (draftId: string, subject: string) => void;
}
