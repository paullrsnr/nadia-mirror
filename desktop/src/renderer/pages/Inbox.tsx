import { useState, useEffect } from "react";
import EmailCard from "../components/EmailCard";
import { Email, getEmails, triggerSync, waitForSync, archiveEmail, getThreadEmails, classifyEmail, classifyAllEmails, suggestReply, getCategories } from "../services/apis/emails.api";
import { getPendingArchive, confirmArchive, rejectArchive } from "../services/apis/autoArchive.api";
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
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [classifying, setClassifying] = useState(false);
  const [draft, setDraft] = useState<string | null>(null);
  const [drafting, setDrafting] = useState(false);
  const [pendingArchive, setPendingArchive] = useState<Email[]>([]);
  const [categories, setCategories] = useState<{ id: number; name: string }[]>([]);

  useEffect(() => {
    checkAuthAndLoadEmails();
  }, [inboxFilter]);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
  }, []);

  async function checkAuthAndLoadEmails() {
    try {
      const authStatus = await getAuthStatus(inboxFilter);
      setIsAuthenticated(authStatus.is_authenticated);
      if (authStatus.is_authenticated) {
        await loadEmails();
        const pending = await getPendingArchive();
        setPendingArchive(pending.emails);
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
      await triggerSync(100, inboxFilter);
      waitForSync(
        async () => {
          await loadEmails();
          const pending = await getPendingArchive();
          setPendingArchive(pending.emails);
          setSyncing(false);
        },
        (msg) => {
          setError(msg);
          setSyncing(false);
        },
      );
    } catch {
      setError("Erreur lors de la synchronisation");
      setSyncing(false);
    }
  }

  async function handleEmailClick(email: Email) {
    setSelectedEmail(email);
    setSummary(null);
    setDraft(null);
    setThreadCount(1);
    if (email.thread_id) {
      try {
        const thread = await getThreadEmails(email.thread_id);
        const ids = new Set(thread.emails.map((e) => e.id));
        setThreadCount(ids.has(email.id) ? thread.count : thread.count + 1);
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

  async function handleClassify(email: Email) {
    setClassifying(true);
    try {
      const result = await classifyEmail(email.id);
      setEmails(emails.map((e) => e.id === email.id ? { ...e, category: result.category } : e));
      if (selectedEmail?.id === email.id) {
        setSelectedEmail({ ...email, category: result.category });
      }
    } catch {
      setError("Erreur lors de la classification. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setClassifying(false);
    }
  }

  async function handleClassifyAll() {
    setClassifying(true);
    setError(null);
    try {
      const result = await classifyAllEmails(20);
      if (result.classified > 0) {
        await loadEmails();
      }
    } catch {
      setError("Erreur lors de la classification. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setClassifying(false);
    }
  }

  async function handleConfirmArchive(email: Email) {
    await confirmArchive(email.id);
    setPendingArchive((prev) => prev.filter((e) => e.id !== email.id));
    setEmails((prev) => prev.filter((e) => e.id !== email.id));
    if (selectedEmail?.id === email.id) setSelectedEmail(null);
  }

  async function handleRejectArchive(email: Email) {
    await rejectArchive(email.id);
    setPendingArchive((prev) => prev.filter((e) => e.id !== email.id));
  }

  async function handleSuggestReply(email: Email) {
    setDrafting(true);
    setDraft(null);
    try {
      const result = await suggestReply(email.id);
      if (result.important && result.draft) {
        setDraft(result.draft);
      } else {
        setDraft("Cet email ne semble pas nécessiter de réponse.");
      }
    } catch {
      setDraft("Erreur lors de la génération du brouillon. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setDrafting(false);
    }
  }

  async function handleSummarizeThread(email: Email) {
    if (!email.thread_id) return;
    setSummarizing(true);
    setSummary(null);
    try {
      const thread = await getThreadEmails(email.thread_id);
      const threadMap = new Map(thread.emails.map((e) => [e.id, e]));
      threadMap.set(email.id, email);
      const threadEmails = Array.from(threadMap.values()).sort(
        (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
      );
      const messages = threadEmails.map((e) => ({
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
      await archiveEmail(email.id, archiveProvider as MailProvider);
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
          <div style={{ display: "flex", gap: spacing.sm, flexWrap: "wrap" }}>
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
            <button
              onClick={handleClassifyAll}
              disabled={classifying || syncing}
              style={{
                padding: `${spacing.sm}px 16px`,
                backgroundColor: colors.backgroundMuted,
                color: colors.textSecondary,
                border: `1px solid ${colors.borderStrong}`,
                borderRadius: radius.sm,
                cursor: classifying ? "not-allowed" : "pointer",
              }}
            >
              {classifying ? "Classification..." : "Classifier (IA)"}
            </button>
          </div>
          <div style={{ marginTop: spacing.sm }}>
            <label>
              Catégorie :
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
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

        {pendingArchive.length > 0 && (
          <div style={{ borderBottom: `1px solid ${colors.borderStrong}`, backgroundColor: colors.backgroundMuted }}>
            <div style={{ padding: `${spacing.sm}px ${spacing.page}px`, fontSize: "12px", color: colors.textSecondary, fontWeight: 600 }}>
              L'IA suggère d'archiver {pendingArchive.length} email{pendingArchive.length > 1 ? "s" : ""}
            </div>
            {pendingArchive.map((email) => (
              <div key={email.id} style={{ padding: `${spacing.sm}px ${spacing.page}px`, borderTop: `1px solid ${colors.borderStrong}`, display: "flex", justifyContent: "space-between", alignItems: "center", gap: spacing.sm }}>
                <div style={{ flex: 1, overflow: "hidden" }}>
                  <div style={{ fontSize: "13px", fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{email.subject || "[Sans objet]"}</div>
                  <div style={{ fontSize: "11px", color: colors.textMuted }}>{email.from_address.name || email.from_address.email}</div>
                </div>
                <div style={{ display: "flex", gap: spacing.sm, flexShrink: 0 }}>
                  <button onClick={() => handleConfirmArchive(email)} style={{ padding: "4px 10px", fontSize: "12px", backgroundColor: colors.buttonPrimary, color: colors.background, border: "none", borderRadius: radius.sm, cursor: "pointer" }}>
                    Archiver
                  </button>
                  <button onClick={() => handleRejectArchive(email)} style={{ padding: "4px 10px", fontSize: "12px", backgroundColor: "transparent", color: colors.textSecondary, border: `1px solid ${colors.borderStrong}`, borderRadius: radius.sm, cursor: "pointer" }}>
                    Garder
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {loading ? (
          <div style={{ padding: spacing.page, textAlign: "center" }}>Chargement...</div>
        ) : emails.length === 0 ? (
          <div style={{ padding: spacing.page, textAlign: "center", color: colors.textMuted }}>
            Aucun email
          </div>
        ) : (
          emails
            .filter((e) => categoryFilter === "all" || e.category === categoryFilter)
            .map((email) => (
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
            <div style={{ display: "flex", gap: spacing.sm, marginBottom: spacing.md, flexWrap: "wrap" }}>
              <button
                onClick={() => handleClassify(selectedEmail)}
                disabled={classifying || summarizing}
                style={{
                  padding: `${spacing.sm}px 16px`,
                  backgroundColor: colors.backgroundMuted,
                  color: colors.textSecondary,
                  border: `1px solid ${colors.borderStrong}`,
                  borderRadius: radius.sm,
                  cursor: classifying ? "not-allowed" : "pointer",
                }}
              >
                {classifying
                  ? "Classification..."
                  : selectedEmail.category
                  ? `Catégorie : ${selectedEmail.category}`
                  : "Classifier avec l'IA"}
              </button>
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
              <button
                onClick={() => handleSuggestReply(selectedEmail)}
                disabled={drafting || summarizing}
                style={{
                  padding: `${spacing.sm}px 16px`,
                  backgroundColor: colors.backgroundMuted,
                  color: colors.textSecondary,
                  border: `1px solid ${colors.borderStrong}`,
                  borderRadius: radius.sm,
                  cursor: drafting ? "not-allowed" : "pointer",
                }}
              >
                {drafting ? "Analyse en cours..." : "Suggérer une réponse (IA)"}
              </button>
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
            {(draft ?? selectedEmail.draft_reply) && (
              <div
                style={{
                  padding: spacing.card,
                  backgroundColor: colors.backgroundMuted,
                  borderRadius: radius.sm,
                  marginBottom: spacing.md,
                  borderLeft: `3px solid ${colors.textSecondary}`,
                }}
              >
                <strong style={{ fontSize: "12px", color: colors.textSecondary }}>BROUILLON DE RÉPONSE</strong>
                <p style={{ margin: `${spacing.xs}px 0 0`, whiteSpace: "pre-wrap" }}>{draft ?? selectedEmail.draft_reply}</p>
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
