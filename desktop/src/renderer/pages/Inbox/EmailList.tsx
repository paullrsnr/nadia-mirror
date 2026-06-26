import "./EmailList.css";
import EmailCard from "../../components/domain/EmailCard";
import Button from "../../components/ui/Button";
import ErrorMessage from "../../components/ui/ErrorMessage";
import type { EmailListProps } from "../../models/email";
import { UNREAD_LABEL } from "../../constants/labels";

export default function EmailList({
  emails,
  pendingArchive,
  loading,
  syncing,
  classifying,
  error,
  folder,
  categoryFilter,
  searchValue,
  selectedEmailId,
  onSync,
  onClassifyAll,
  onEmailClick,
  onArchive,
  onToggleStar,
  onConfirmArchive,
  onRejectArchive,
}: EmailListProps) {
  const search = searchValue.trim().toLowerCase();

  const filtered = emails.filter((e) => {
    if (folder === "favoris" && !e.is_starred) return false;
    if (categoryFilter !== "all" && e.category !== categoryFilter) return false;
    if (!search) return true;
    const haystack = `${e.subject} ${e.snippet ?? ""} ${e.from_address.name ?? ""} ${e.from_address.email}`.toLowerCase();
    return haystack.includes(search);
  });

  const unreadCount = filtered.filter((e) => e.labels.includes(UNREAD_LABEL)).length;

  return (
    <div className="email-list scrollbar-hidden">
      <div className="email-list__header">
        <h3 className="email-list__title">
          {folder === "favoris" ? "Favoris" : folder === "sent" ? "Envoyés" : "Boîte de réception"}
        </h3>
        <span className="email-list__unread">{unreadCount} non lus</span>
      </div>

      {folder !== "sent" && (
        <div className="email-list__toolbar">
          <div className="email-list__actions">
            <Button size="sm" onClick={() => onSync(false)} disabled={syncing}>
              {syncing ? "Synchronisation..." : "Synchroniser"}
            </Button>
            <Button size="sm" variant="secondary" onClick={() => onSync(true)} disabled={syncing}>
              {syncing ? "Synchronisation..." : "Sync. complète (30j)"}
            </Button>
            <Button size="sm" variant="secondary" onClick={onClassifyAll} disabled={classifying || syncing}>
              {classifying ? "Classification..." : "Classifier (IA)"}
            </Button>
          </div>
        </div>
      )}

      {folder === "inbox" && pendingArchive.length > 0 && (
        <div className="email-list__pending">
          <div className="email-list__pending-header">
            L'IA suggère d'archiver {pendingArchive.length} email
            {pendingArchive.length > 1 ? "s" : ""}
          </div>
          {pendingArchive.map((email) => (
            <div key={email.id} className="email-list__pending-item">
              <div className="email-list__pending-info">
                <div className="email-list__pending-subject">
                  {email.subject || "[Sans objet]"}
                </div>
                <div className="email-list__pending-from">
                  {email.from_address.name || email.from_address.email}
                </div>
              </div>
              <div className="email-list__pending-actions">
                <Button size="sm" onClick={() => onConfirmArchive(email)}>
                  Archiver
                </Button>
                <Button size="sm" variant="ghost" onClick={() => onRejectArchive(email)}>
                  Garder
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="email-list__items scrollbar-hidden">
        {loading ? (
          <div className="email-list__empty">Chargement...</div>
        ) : filtered.length === 0 ? (
          <div className="email-list__empty">Aucun email</div>
        ) : (
          filtered.map((email) => (
            <EmailCard
              key={email.id}
              email={email}
              isSelected={email.id === selectedEmailId}
              onClick={() => onEmailClick(email)}
              onArchive={() => onArchive(email)}
              onToggleStar={() => onToggleStar(email)}
            />
          ))
        )}
      </div>

      {error && <ErrorMessage message={error} className="email-list__error" />}
    </div>
  );
}
