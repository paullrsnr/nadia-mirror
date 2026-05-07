import EmailCard from "../../components/domain/EmailCard";
import Button from "../../components/ui/Button";
import ErrorMessage from "../../components/ui/ErrorMessage";
import { colors, spacing } from "../../styles";
import type { Email, Category, MailProvider } from "../../types";

interface EmailListProps {
  emails: Email[];
  pendingArchive: Email[];
  categories: Category[];
  loading: boolean;
  syncing: boolean;
  classifying: boolean;
  error: string | null;
  provider: MailProvider;
  categoryFilter: string;
  onProviderChange: (p: MailProvider) => void;
  onCategoryFilterChange: (cat: string) => void;
  onSync: (full: boolean) => void;
  onClassifyAll: () => void;
  onEmailClick: (email: Email) => void;
  onArchive: (email: Email) => void;
  onConfirmArchive: (email: Email) => void;
  onRejectArchive: (email: Email) => void;
}

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
    <div
      style={{
        width: "40%",
        borderRight: `1px solid ${colors.borderStrong}`,
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Toolbar */}
      <div
        style={{
          padding: spacing.page,
          borderBottom: `1px solid ${colors.borderStrong}`,
          backgroundColor: colors.backgroundMuted,
        }}
      >
        <h1 style={{ margin: 0, marginBottom: spacing.md }}>Nadia</h1>

        <div style={{ marginBottom: spacing.sm }}>
          <label>
            Boîte mail :
            <select
              value={provider}
              onChange={(e) => onProviderChange(e.target.value as MailProvider)}
              style={{ marginLeft: spacing.sm }}
            >
              <option value="all">Toutes les boîtes</option>
              <option value="gmail">Gmail</option>
              <option value="outlook">Outlook</option>
            </select>
          </label>
        </div>

        <div style={{ display: "flex", gap: spacing.sm, flexWrap: "wrap" }}>
          <Button onClick={() => onSync(false)} disabled={syncing}>
            {syncing ? "Synchronisation..." : "Synchroniser"}
          </Button>
          <Button variant="secondary" onClick={() => onSync(true)} disabled={syncing}>
            {syncing ? "Synchronisation..." : "Sync. complète (30j)"}
          </Button>
          <Button
            variant="secondary"
            onClick={onClassifyAll}
            disabled={classifying || syncing}
          >
            {classifying ? "Classification..." : "Classifier (IA)"}
          </Button>
        </div>

        <div style={{ marginTop: spacing.sm }}>
          <label>
            Catégorie :
            <select
              value={categoryFilter}
              onChange={(e) => onCategoryFilterChange(e.target.value)}
              style={{ marginLeft: spacing.sm }}
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

      {/* Suggestions d'archivage */}
      {pendingArchive.length > 0 && (
        <div
          style={{
            borderBottom: `1px solid ${colors.borderStrong}`,
            backgroundColor: colors.backgroundMuted,
          }}
        >
          <div
            style={{
              padding: `${spacing.sm} ${spacing.page}`,
              fontSize: "12px",
              color: colors.textSecondary,
              fontWeight: 600,
            }}
          >
            L'IA suggère d'archiver {pendingArchive.length} email
            {pendingArchive.length > 1 ? "s" : ""}
          </div>
          {pendingArchive.map((email) => (
            <div
              key={email.id}
              style={{
                padding: `${spacing.sm} ${spacing.page}`,
                borderTop: `1px solid ${colors.borderStrong}`,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: spacing.sm,
              }}
            >
              <div style={{ flex: 1, overflow: "hidden" }}>
                <div
                  style={{
                    fontSize: "13px",
                    fontWeight: 500,
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {email.subject || "[Sans objet]"}
                </div>
                <div style={{ fontSize: "11px", color: colors.textMuted }}>
                  {email.from_address.name || email.from_address.email}
                </div>
              </div>
              <div style={{ display: "flex", gap: spacing.sm, flexShrink: 0 }}>
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

      {/* Liste */}
      {loading ? (
        <div style={{ padding: spacing.page, textAlign: "center", color: colors.textMuted }}>
          Chargement...
        </div>
      ) : filtered.length === 0 ? (
        <div style={{ padding: spacing.page, textAlign: "center", color: colors.textMuted }}>
          Aucun email
        </div>
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

      {error && (
        <ErrorMessage
          message={error}
          style={{ margin: spacing.page }}
        />
      )}
    </div>
  );
}
