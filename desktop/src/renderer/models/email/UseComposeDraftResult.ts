import type { RefObject } from "react";
import type { EmailAttachment } from "./EmailAttachment";

export interface UseComposeDraftResult {
  to: string;
  cc: string;
  bcc: string;
  subject: string;
  bodyRef: RefObject<HTMLDivElement | null>;
  initialBodyHtml: string;
  setTo: (value: string) => void;
  setCc: (value: string) => void;
  setBcc: (value: string) => void;
  setSubject: (value: string) => void;
  handleBodyInput: () => void;
  saving: boolean;
  sending: boolean;
  sendError: string | null;
  attachments: EmailAttachment[];
  uploadingAttachment: boolean;
  handleAddAttachments: (files: FileList) => void;
  handleRemoveAttachment: (attachmentId: string) => void;
  ccVisible: boolean;
  bccVisible: boolean;
  showCc: () => void;
  showBcc: () => void;
  execFormat: (command: string, value?: string) => void;
  resetTextColor: () => void;
  toggleHighlight: (color: string) => void;
  resetHighlight: () => void;
  handleSend: () => Promise<void>;
  handleClose: () => void;
}
