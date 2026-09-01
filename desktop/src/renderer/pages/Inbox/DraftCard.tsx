import "./DraftCard.css";
import { IconTrash } from "../../components/ui/icons";
import type { DraftCardProps } from "../../models";

export default function DraftCard({ draft, onClick, onDelete }: DraftCardProps) {
  const to = draft.to_addresses.map((a) => a.name || a.email).join(", ");
  const date = new Date(draft.updated_at).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="draft-card" onClick={onClick} role="button" tabIndex={0}>
      <div className="draft-card__main">
        <div className="draft-card__meta">
          <span className="draft-card__to">{to || "(Aucun destinataire)"}</span>
          <span className="draft-card__date">{date}</span>
        </div>
        <div className="draft-card__subject">{draft.subject || "[Sans objet]"}</div>
        {draft.body_text && <div className="draft-card__snippet">{draft.body_text}</div>}
      </div>
      <button
        type="button"
        className="draft-card__delete"
        title="Supprimer le brouillon"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        <IconTrash />
      </button>
    </div>
  );
}
