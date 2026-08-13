import "./EmailDetailBody.css";
import type { EmailDetailBodyProps } from "../../../models/email";
import EmailHtmlBody, { isRichHtml } from "../../../components/domain/EmailHtmlBody";

export default function EmailDetailBody({ email }: EmailDetailBodyProps) {
  if (email.body_html && isRichHtml(email.body_html)) {
    return (
      <div className="email-detail-body email-detail-body--html">
        <EmailHtmlBody html={email.body_html} />
      </div>
    );
  }

  return <div className="email-detail-body">{email.body_text}</div>;
}
