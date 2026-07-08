import type { EmailCardProps } from "../../../models/email";
import { IconAttachment } from "../../ui/icons";
import Button from "../../ui/Button";
import StarButton from "../../ui/StarButton";
import { UNREAD_LABEL } from "../../../constants/labels";
import "./EmailCard.css";

export default function EmailCard({ email, isSelected, onClick, onArchive, onToggleStar }: EmailCardProps) {
  const isUnread = email.labels.includes(UNREAD_LABEL);
  const fromName = email.from_address.name || email.from_address.email;
  const date = new Date(email.date).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  const classNames = ["root"];
  if (isUnread) classNames.push("root--unread");
  if (isSelected) classNames.push("root--selected");

  return (
    <div
      className={classNames.join(" ")}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick();
        }
      }}
    >
      <div className="row">
        <StarButton starred={!!email.is_starred} onToggle={() => onToggleStar?.()} />
        <div className="main">
          <div className="meta">
            <span className="from">{fromName}</span>
            <span className="date">{date}</span>
          </div>
          <div className="subject">
            {email.subject || "[Sans objet]"}
            {email.attachments.length > 0 && <IconAttachment className="attachment-indicator" />}
          </div>
          {email.snippet && <div className="snippet truncate">{email.snippet}</div>}
          {(email.category || onArchive) && (
            <div className="footer">
              {email.category && (
                <span className={`category-badge category-badge--${email.category}`}>
                  {email.category}
                </span>
              )}
              {onArchive && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onArchive();
                  }}
                >
                  Archiver
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
