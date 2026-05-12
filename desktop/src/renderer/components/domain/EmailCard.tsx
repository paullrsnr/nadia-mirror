import type { EmailCardProps } from "../../models/email";
import Button from "../ui/Button";
import "./EmailCard.css";

export default function EmailCard({ email, onClick, onArchive }: EmailCardProps) {
  const isUnread = email.labels.includes("UNREAD");
  const fromName = email.from_address.name || email.from_address.email;
  const date = new Date(email.date).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className={isUnread ? "root root--unread" : "root"}
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
        <div className="main">
          <div className="meta">
            <span className="text-primary">{fromName}</span>
            {email.category && (
              <span className={`category-badge category-badge--${email.category}`}>
                {email.category}
              </span>
            )}
          </div>
          <div className="text-secondary subject">{email.subject || "[Sans objet]"}</div>
          {email.snippet && (
            <div className="snippet text-muted truncate">{email.snippet}</div>
          )}
        </div>
        <div className="aside">
          <span className="text-muted">{date}</span>
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
      </div>
    </div>
  );
}
