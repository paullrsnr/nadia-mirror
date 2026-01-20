 import React from "react";
import { Email } from "../services/apis/emails.api";

interface EmailCardProps {
  email: Email;
  onClick: () => void;
  onArchive?: () => void;
}

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

  return (
    <div
      onClick={onClick}
      style={{
        padding: 15,
        borderBottom: "1px solid #eee",
        cursor: "pointer",
        backgroundColor: isUnread ? "#f0f7ff" : "white",
        fontWeight: isUnread ? "bold" : "normal",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = "#f5f5f5";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = isUnread ? "#f0f7ff" : "white";
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontWeight: "bold", color: "#333" }}>{fromName}</span>
          </div>
          <div style={{ marginTop: 5, color: "#666", fontSize: "14px" }}>
            {email.subject || "[Sans objet]"}
          </div>
          {email.snippet && (
            <div
              style={{
                marginTop: 5,
                color: "#888",
                fontSize: "12px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {email.snippet}
            </div>
          )}
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 5 }}>
          <span style={{ fontSize: "12px", color: "#888" }}>{date}</span>
          {onArchive && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onArchive();
              }}
              style={{
                padding: "4px 8px",
                fontSize: "11px",
                border: "1px solid #ccc",
                borderRadius: "3px",
                cursor: "pointer",
                backgroundColor: "white",
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
