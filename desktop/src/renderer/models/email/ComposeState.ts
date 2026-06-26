import type { Email } from "./Email";
import type { DraftEmail } from "./DraftEmail";

export type ComposeMode = "new" | "reply" | "forward" | "draft";

export interface ComposeState {
  open: boolean;
  mode: ComposeMode;
  replyTo?: Email;
  draft?: DraftEmail;
}
