import "./EmailList.css";
import DraftCard from "./DraftCard";
import ErrorMessage from "../../components/ui/ErrorMessage";
import type { DraftEmail } from "../../models";

interface DraftsListProps {
  drafts: DraftEmail[];
  loading: boolean;
  error: string | null;
  onDraftClick: (draft: DraftEmail) => void;
  onDraftDelete: (draft: DraftEmail) => void;
}

export default function DraftsList({ drafts, loading, error, onDraftClick, onDraftDelete }: DraftsListProps) {
  return (
    <div className="email-list">
      <div className="email-list__header">
        <h3 className="email-list__title">Brouillons</h3>
      </div>

      <div className="email-list__items">
        {loading ? (
          <div className="email-list__empty">Chargement...</div>
        ) : drafts.length === 0 ? (
          <div className="email-list__empty">Aucun brouillon</div>
        ) : (
          drafts.map((draft) => (
            <DraftCard
              key={draft.id}
              draft={draft}
              onClick={() => onDraftClick(draft)}
              onDelete={() => onDraftDelete(draft)}
            />
          ))
        )}
      </div>

      {error && <ErrorMessage message={error} className="email-list__error" />}
    </div>
  );
}
