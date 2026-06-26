import type { EmailAddress } from "./EmailAddress";
import type { EmailAttachment } from "./EmailAttachment";

export interface DraftEmail {
  id: string;
  provider: string;
  to_addresses: EmailAddress[];
  cc_addresses: EmailAddress[];
  bcc_addresses: EmailAddress[];
  subject: string;
  body_text: string;
  body_html?: string;
  updated_at: string;
  in_reply_to_email_id?: string;
  attachments: EmailAttachment[];
}
