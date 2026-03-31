import React, { useState, useEffect } from "react";
import EmailCard from "../components/EmailCard";
import { Email, getEmails, syncEmails, archiveEmail, getThreadEmails } from "../services/apis/emails.api";
import { getAuthStatus, type MailProvider } from "../services/apis/auth.api";
import { summarizeEmail, summarizeThread } from "../services/apis/llm.api";
import { colors, spacing, radius } from "../theme";

const DEFAULT_INBOX_VIEW: MailProvider = "all";

export default function Inbox() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [inboxFilter, setInboxFilter] = useState<MailProvider>(DEFAULT_INBOX_VIEW);
  const [summary, setSummary] = useState<string | null>(null);
  const [summarizing, setSummarizing] = useState(false);
  const [threadCount, setThreadCount] = useState<number>(1);

  useEffect(() => {
    checkAuthAndLoadEmails();
  }, [inboxFilter]);

  async function checkAuthAndLoadEmails() {
    try {
      const authStatus = await getAuthStatus(inboxFilter);
      setIsAuthenticated(authStatus.is_authenticated);
      if (authStatus.is_authenticated) {
        await loadEmails();
      }
    } catch {
      setError("Erreur de connexion");
    }
  }

  async function loadEmails() {
    setLoading(true);
    setError(null);
    try {
      const response = await getEmails(50, inboxFilter);
      setEmails(response.emails);
    } catch (err) {
      setError("Erreur lors du chargement des emails");
    } finally {
      setLoading(false);
    }
  }

  async function handleSync() {
    setSyncing(true);
    setError(null);
    try {
      const result = await syncEmails(100, inboxFilter);
      if (result.status === "error") {
        setError(result.message ?? "Erreur lors de la synchronisation");
      } else {
        await loadEmails();
      }
    } catch (err) {
      setError("Erreur lors de la synchronisation");
    } finally {
      setSyncing(false);
    }
  }

  async function handleEmailClick(email: Email) {
    setSelectedEmail(email);
    setSummary(null);
    setThreadCount(1);
    if (email.thread_id) {
      try {
        const thread = await getThreadEmails(email.thread_id);
        setThreadCount(thread.count);
      } catch {
        // silencieux — le bouton thread sera simplement masqué
      }
    }
  }

  async function handleSummarize(email: Email) {
    setSummarizing(true);
    setSummary(null);
    try {
      const result = await summarizeEmail(
        email.subject ?? "",
        email.body_text ?? "",
        email.from_address.email
      );
      setSummary(result.summary);
    } catch {
      setSummary("Erreur lors du résumé. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setSummarizing(false);
    }
  }

  async function handleSummarizeThread(email: Email) {
    if (!email.thread_id) return;
    setSummarizing(true);
    setSummary(null);
    try {
      const thread = await getThreadEmails(email.thread_id);
      const messages = thread.emails.map((e) => ({
        from_address: e.from_address.email,
        body: e.body_text ?? "",
        date: e.date ? new Date(e.date).toLocaleString("fr-FR") : "",
      }));
      const result = await summarizeThread(email.subject ?? "", messages);
      setSummary(result.summary);
    } catch {
      setSummary("Erreur lors du résumé. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setSummarizing(false);
    }
  }

  async function handleArchive(email: Email) {
    const archiveProvider = inboxFilter === "all" ? (email.provider ?? "gmail") : inboxFilter;
    if (archiveProvider === "all") return;
    try {
      await archiveEmail(email.id, archiveProvider);
      setEmails(emails.filter((e) => e.id !== email.id));
      if (selectedEmail?.id === email.id) {
        setSelectedEmail(null);
      }
    } catch (err) {
      setError("Erreur lors de l'archivage");
    }
  }

  if (!isAuthenticated) {
    return (
      <div style={{ padding: spacing.page, textAlign: "center" }}>
        <h1>📬 Nadia</h1>
        <p>Veuillez vous connecter à votre boîte mail dans les paramètres.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Liste des emails */}
      <div style={{ width: "40%", borderRight: `1px solid ${colors.borderStrong}`, overflowY: "auto" }}>
        <div style={{ padding: spacing.page, borderBottom: `1px solid ${colors.borderStrong}`, backgroundColor: colors.backgroundMuted }}>
          <h1 style={{ margin: 0, marginBottom: spacing.md }}>📬 Nadia</h1>
          <div style={{ marginBottom: spacing.sm }}>
            <label>
              Boîte mail :
              <select
                value={inboxFilter}
                onChange={(e) => {
                  setSelectedEmail(null);
                  setEmails([]);
                  setInboxFilter(e.target.value as MailProvider);
                }}
                style={{ marginLeft: spacing.sm }}
              >
                <option value="all">Toutes les boîtes</option>
                <option value="gmail">Gmail</option>
                <option value="outlook">Outlook</option>
              </select>
            </label>
          </div>
          <button
            onClick={handleSync}
            disabled={syncing}
            style={{
              padding: `${spacing.sm}px 16px`,
              backgroundColor: colors.buttonPrimary,
              color: colors.background,
              border: "none",
              borderRadius: radius.sm,
              cursor: syncing ? "not-allowed" : "pointer",
            }}
          >
            {syncing ? "Synchronisation..." : "Synchroniser"}
          </button>
        </div>

        {loading ? (
          <div style={{ padding: spacing.page, textAlign: "center" }}>Chargement...</div>
        ) : emails.length === 0 ? (
          <div style={{ padding: spacing.page, textAlign: "center", color: colors.textMuted }}>
            Aucun email
          </div>
        ) : (
          emails.map((email) => (
            <EmailCard
              key={email.id}
              email={email}
              onClick={() => handleEmailClick(email)}
              onArchive={() => handleArchive(email)}
            />
          ))
        )}

        {error && (
          <div style={{ padding: spacing.page, color: colors.error, textAlign: "center" }}>
            {error}
          </div>
        )}
      </div>

      {/* Détails de l'email */}
      <div style={{ flex: 1, overflowY: "auto", padding: spacing.page }}>
        {selectedEmail ? (
          <div>
            <h2>{selectedEmail.subject || "[Sans objet]"}</h2>
            <div style={{ color: colors.textSecondary, marginBottom: spacing.md }}>
              <div>
                <strong>De:</strong> {selectedEmail.from_address.name || selectedEmail.from_address.email}
              </div>
              <div>
                <strong>Date:</strong>{" "}
                {new Date(selectedEmail.date).toLocaleString("fr-FR")}
              </div>
            </div>
            <div style={{ display: "flex", gap: spacing.sm, marginBottom: spacing.md }}>
              <button
                onClick={() => handleSummarize(selectedEmail)}
                disabled={summarizing}
                style={{
                  padding: `${spacing.sm}px 16px`,
                  backgroundColor: colors.buttonPrimary,
                  color: colors.background,
                  border: "none",
                  borderRadius: radius.sm,
                  cursor: summarizing ? "not-allowed" : "pointer",
                }}
              >
                {summarizing ? "Résumé en cours..." : "Résumer avec l'IA"}
              </button>
              {threadCount > 1 && (
                <button
                  onClick={() => handleSummarizeThread(selectedEmail)}
                  disabled={summarizing}
                  style={{
                    padding: `${spacing.sm}px 16px`,
                    backgroundColor: colors.buttonPrimary,
                    color: colors.background,
                    border: "none",
                    borderRadius: radius.sm,
                    cursor: summarizing ? "not-allowed" : "pointer",
                  }}
                >
                  {summarizing ? "Résumé en cours..." : `Résumer la discussion (${threadCount} messages)`}
                </button>
              )}
            </div>
            {summary && (
              <div
                style={{
                  padding: spacing.card,
                  backgroundColor: colors.backgroundMuted,
                  borderRadius: radius.sm,
                  marginBottom: spacing.md,
                  borderLeft: `3px solid ${colors.buttonPrimary}`,
                }}
              >
                <strong style={{ fontSize: "12px", color: colors.textSecondary }}>RÉSUMÉ IA</strong>
                <p style={{ margin: `${spacing.xs}px 0 0`, whiteSpace: "pre-wrap" }}>{summary}</p>
              </div>
            )}
            <div style={{ marginTop: spacing.page, whiteSpace: "pre-wrap" }}>
              {selectedEmail.body_text}
            </div>
          </div>
        ) : (
          <div style={{ textAlign: "center", color: colors.textMuted, marginTop: spacing.lg }}>
            Sélectionnez un email pour voir les détails
          </div>
        )}
      </div>
    </div>
  );
}
