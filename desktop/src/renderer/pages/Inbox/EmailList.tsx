import "./EmailList.css";
import EmailCard from "../../components/domain/EmailCard";
import Button from "../../components/ui/Button";
import ErrorMessage from "../../components/ui/ErrorMessage";
import type { EmailListProps } from "../../models/email";
import type { MailProvider } from "../../models/auth";

export default function EmailList({
  emails,
  pendingArchive,
  categories,
  loading,
  syncing,
  classifying,
  error,
  provider,
  categoryFilter,
  onProviderChange,
  onCategoryFilterChange,
  onSync,
  onClassifyAll,
  onEmailClick,
  onArchive,
  onConfirmArchive,
  onRejectArchive,
}: EmailListProps) {
  const filtered = emails.filter(
    (e) => categoryFilter === "all" || e.category === categoryFilter,
  );

  return (
    <div className="email-list">
      <div className="email-list__toolbar">
        <h1 className="email-list__toolbar-title">Nadia</h1>

        <div className="email-list__filter-row">
          <label>
            Boîte mail :
            <select
              value={provider}
              onChange={(e) => onProviderChange(e.target.value as MailProvider)}
            >
              <option value="all">Toutes les boîtes</option>
              <option value="gmail">Gmail</option>
              <option value="outlook">Outlook</option>
            </select>
          </label>
        </div>

        <div className="email-list__actions">
          <Button onClick={() => onSync(false)} disabled={syncing}>
            {syncing ? "Synchronisation..." : "Synchroniser"}
          </Button>
          <Button variant="secondary" onClick={() => onSync(true)} disabled={syncing}>
            {syncing ? "Synchronisation..." : "Sync. complète (30j)"}
          </Button>
          <Button variant="secondary" onClick={onClassifyAll} disabled={classifying || syncing}>
            {classifying ? "Classification..." : "Classifier (IA)"}
          </Button>
        </div>

        <div className="email-list__category-filter">
          <label>
            Catégorie :
            <select
              value={categoryFilter}
              onChange={(e) => onCategoryFilterChange(e.target.value)}
            >
              <option value="all">Toutes</option>
              {categories.map((c) => (
                <option key={c.id} value={c.name}>
                  {c.name.charAt(0).toUpperCase() + c.name.slice(1)}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {pendingArchive.length > 0 && (
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

      {loading ? (
        <div className="email-list__empty">Chargement...</div>
      ) : filtered.length === 0 ? (
        <div className="email-list__empty">Aucun email</div>
      ) : (
        filtered.map((email) => (
          <EmailCard
            key={email.id}
            email={email}
            onClick={() => onEmailClick(email)}
            onArchive={() => onArchive(email)}
          />
        ))
      )}

      {error && <ErrorMessage message={error} className="email-list__error" />}
    </div>
  );
}
