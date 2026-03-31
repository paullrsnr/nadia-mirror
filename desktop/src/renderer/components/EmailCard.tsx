import React from "react";
import type { EmailCardProps } from "../models";
import "./EmailCard.css";

export default function EmailCard({
  email,
  onClick,
  onArchive,
}: EmailCardProps) {
  const isUnread = email.labels.includes("UNREAD");
  const fromName = email.from_address.name || email.from_address.email;
  const date = new Date(email.date).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  const rootClass = isUnread
    ? `root root--unread`
    : `root`;

  return (
    <div
      className={rootClass}
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
          <div className={`text-secondary subject`}>
            {email.subject || "[Sans objet]"}
          </div>
          {email.snippet && (
            <div className={`snippet text-muted truncate`}>
              {email.snippet}
            </div>
          )}
        </div>
        <div className="aside">
          <span className="text-muted">{date}</span>
          {onArchive && (
            <button
              type="button"
              className="btn-secondary"
              onClick={(e) => {
                e.stopPropagation();
                onArchive();
              }}
            >
              Archiver
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
