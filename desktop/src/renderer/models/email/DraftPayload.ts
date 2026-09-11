import type { ConnectableProvider } from "../auth/ConnectableProvider";

export interface DraftPayload {
  provider: ConnectableProvider;
  to: string[];
  cc: string[];
  bcc: string[];
  subject: string;
  body_text: string;
  body_html?: string;
  in_reply_to_email_id?: string;
}
