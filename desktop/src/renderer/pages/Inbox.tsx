import React, { useState, useEffect } from "react";
import EmailCard from "../components/EmailCard";
import { Email, getEmails, syncEmails, archiveEmail } from "../services/apis/emails.api";
import { getAuthStatus } from "../services/apis/auth.api";
import { colors, spacing, radius } from "../theme";

export default function Inbox() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthAndLoad();
  }, []);

  async function checkAuthAndLoad() {
    try {
      const authStatus = await getAuthStatus();
      setIsAuthenticated(authStatus.is_authenticated);
      
      if (authStatus.is_authenticated) {
        await loadEmails();
      }
    } catch (err) {
      setError("Erreur de connexion");
    }
  }

  async function loadEmails() {
    setLoading(true);
    setError(null);
    try {
      const response = await getEmails(50);
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
      const result = await syncEmails(100);
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
  }

  async function handleArchive(emailId: string) {
    try {
      await archiveEmail(emailId);
      setEmails(emails.filter((e) => e.id !== emailId));
      if (selectedEmail?.id === emailId) {
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
        <p>Veuillez vous connecter à Gmail dans les paramètres.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Liste des emails */}
      <div style={{ width: "40%", borderRight: `1px solid ${colors.borderStrong}`, overflowY: "auto" }}>
        <div style={{ padding: spacing.page, borderBottom: `1px solid ${colors.borderStrong}`, backgroundColor: colors.backgroundMuted }}>
          <h1 style={{ margin: 0, marginBottom: spacing.md }}>📬 Nadia</h1>
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
              onArchive={() => handleArchive(email.id)}
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
