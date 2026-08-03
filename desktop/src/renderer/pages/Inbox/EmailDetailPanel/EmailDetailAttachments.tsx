import "./EmailDetailAttachments.css";
import { IconAttachment, IconDownload } from "../../../components/ui/icons";
import { getAttachmentDownloadUrl } from "../../../services/api/emails.api";
import type { EmailDetailAttachmentsProps } from "../../../models/email";
import { formatFileSize } from "../../../helpers";

export default function EmailDetailAttachments({ emailId, attachments }: EmailDetailAttachmentsProps) {
  if (attachments.length === 0) return null;

  return (
    <div className="email-detail-attachments">
      <div className="email-detail-attachments__title">
        <IconAttachment />
        {attachments.length} pièce{attachments.length > 1 ? "s" : ""} jointe
        {attachments.length > 1 ? "s" : ""}
      </div>
      <ul className="email-detail-attachments__list">
        {attachments.map((attachment) => (
          <li key={attachment.attachment_id} className="email-detail-attachments__item">
            <span className="email-detail-attachments__name">{attachment.filename}</span>
            <span className="email-detail-attachments__size">{formatFileSize(attachment.size)}</span>
            <a
              className="email-detail-attachments__download"
              href={getAttachmentDownloadUrl(emailId, attachment.attachment_id)}
              download={attachment.filename}
              title="Télécharger"
            >
              <IconDownload />
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
