import { useState, useEffect } from "react";
import { getAuthUrl, getAuthStatus, logout, AuthStatus } from "../services/apis/auth.api";

export default function Settings() {
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  async function checkAuthStatus() {
    try {
      const status = await getAuthStatus();
      setAuthStatus(status);
    } catch (err) {
      setError("Erreur lors de la vérification du statut");
    }
  }

  async function handleConnectGmail() {
    setLoading(true);
    setError(null);

    try {
      const authUrl = await getAuthUrl();
      // Ouvrir la fenêtre d'authentification
      window.open(authUrl, "_blank", "width=600,height=700");
      
      // Polling pour vérifier si l'authentification a réussi
      const interval = setInterval(async () => {
        try {
          const status = await getAuthStatus();
          if (status.is_authenticated) {
            clearInterval(interval);
            setAuthStatus(status);
            setLoading(false);
          }
        } catch (err) {
          // Continuer le polling
        }
      }, 2000);

      // Arrêter le polling après 5 minutes
      setTimeout(() => {
        clearInterval(interval);
        setLoading(false);
      }, 300000);
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err?.message || "Erreur lors de la connexion à Gmail";
      setError(errorMessage);
      setLoading(false);
    }
  }

  async function handleDisconnect() {
    setLoading(true);
    setError(null);

    try {
      await logout();
      setAuthStatus({ is_authenticated: false, email: null });
    } catch (err) {
      setError("Erreur lors de la déconnexion");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>⚙️ Paramètres</h1>

      <div style={{ marginTop: 30 }}>
        <h2>Connexion Gmail</h2>

        {authStatus?.is_authenticated ? (
          <div>
            <p style={{ color: "green" }}>
              ✓ Connecté {authStatus.email ? `(${authStatus.email})` : ""}
            </p>
            <button onClick={handleDisconnect} disabled={loading}>
              {loading ? "Déconnexion..." : "Déconnecter"}
            </button>
          </div>
        ) : (
          <div>
            <p>Non connecté</p>
            <button onClick={handleConnectGmail} disabled={loading}>
              {loading ? "Connexion..." : "Se connecter à Gmail"}
            </button>
          </div>
        )}

        {error && <p style={{ color: "red", marginTop: 10 }}>{error}</p>}
      </div>
    </div>
  );
}
