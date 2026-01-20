import React, { useState, useEffect } from "react";
import EmailCard from "../components/EmailCard";
import { Email, getEmails, syncEmails, archiveEmail } from "../services/apis/emails.api";
import { getAuthStatus } from "../services/apis/auth.api";

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
      await syncEmails(100, false);
      await loadEmails();
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
      <div style={{ padding: 20, textAlign: "center" }}>
        <h1>📬 Nadia</h1>
        <p>Veuillez vous connecter à Gmail dans les paramètres.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Liste des emails */}
      <div style={{ width: "40%", borderRight: "1px solid #ddd", overflowY: "auto" }}>
        <div style={{ padding: 20, borderBottom: "1px solid #ddd", backgroundColor: "#f9f9f9" }}>
          <h1 style={{ margin: 0, marginBottom: 10 }}>📬 Nadia</h1>
          <button
            onClick={handleSync}
            disabled={syncing}
            style={{
              padding: "8px 16px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: 3,
              cursor: syncing ? "not-allowed" : "pointer",
            }}
          >
            {syncing ? "Synchronisation..." : "Synchroniser"}
          </button>
        </div>

        {loading ? (
          <div style={{ padding: 20, textAlign: "center" }}>Chargement...</div>
        ) : emails.length === 0 ? (
          <div style={{ padding: 20, textAlign: "center", color: "#888" }}>
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
          <div style={{ padding: 20, color: "red", textAlign: "center" }}>
            {error}
          </div>
        )}
      </div>

      {/* Détails de l'email */}
      <div style={{ flex: 1, overflowY: "auto", padding: 20 }}>
        {selectedEmail ? (
          <div>
            <h2>{selectedEmail.subject || "[Sans objet]"}</h2>
            <div style={{ color: "#666", marginBottom: 10 }}>
              <div>
                <strong>De:</strong> {selectedEmail.from_address.name || selectedEmail.from_address.email}
              </div>
              <div>
                <strong>Date:</strong>{" "}
                {new Date(selectedEmail.date).toLocaleString("fr-FR")}
              </div>
            </div>
            <div style={{ marginTop: 20, whiteSpace: "pre-wrap" }}>
              {selectedEmail.body_text}
            </div>
          </div>
        ) : (
          <div style={{ textAlign: "center", color: "#888", marginTop: 50 }}>
            Sélectionnez un email pour voir les détails
          </div>
        )}
      </div>
    </div>
  );
}
