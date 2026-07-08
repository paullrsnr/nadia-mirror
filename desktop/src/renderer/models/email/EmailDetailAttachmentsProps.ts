import type { EmailAttachment } from "./EmailAttachment";

export interface EmailDetailAttachmentsProps {
  emailId: string;
  attachments: EmailAttachment[];
}
