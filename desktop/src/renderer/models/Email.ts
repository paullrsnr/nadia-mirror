import type { EmailAddress } from "./EmailAddress";
import type { EmailAttachment } from "./EmailAttachment";

export interface Email {
  id: string;
  thread_id: string;
  subject: string;
  from_address: EmailAddress;
  to_addresses: EmailAddress[];
  cc_addresses: EmailAddress[];
  date: string;
  body_text: string;
  body_html?: string;
  attachments: EmailAttachment[];
  labels: string[];
  snippet?: string;
  /** Boîte d'origine (gmail | outlook) pour archivage en vue "Toutes les boîtes" */
  provider?: string;
}
