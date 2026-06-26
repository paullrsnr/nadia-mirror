import type { MailProvider } from "../auth/MailProvider";

export interface DraftPayload {
  provider: MailProvider;
  to: string[];
  cc: string[];
  bcc: string[];
  subject: string;
  body_text: string;
  body_html?: string;
  in_reply_to_email_id?: string;
}
