import { useState, useEffect, useCallback } from "react";
import type { ApiError } from "../services/apis/auth.api";
import AuthProviderCard from "../components/AuthProviderCard";
import { colors, spacing } from "../theme";
import {
  getAllAuthStatuses,
  getAuthStatus,
  getAuthUrl,
  logout,
  CONNECTABLE_PROVIDERS,
  type ConnectableProvider,
  type AuthStateByProvider,
} from "../services/auth";

const PROVIDER_LABELS: Record<ConnectableProvider, string> = {
  gmail: "Gmail",
  outlook: "Outlook",
};

/** Intervalle de vérification après ouverture de la fenêtre OAuth (ms). */
const POLL_INTERVAL_MS = 2000;
/** Durée max du polling avant abandon (ms). */
const POLL_TIMEOUT_MS = 300000;

export default function Settings() {
  const [authByProvider, setAuthByProvider] = useState<AuthStateByProvider>({
    gmail: null,
    outlook: null,
  });
  const [loading, setLoading] = useState<Record<ConnectableProvider, boolean>>({
    gmail: false,
    outlook: false,
  });
  const [error, setError] = useState<string | null>(null);

  const refreshAllAuthStatuses = useCallback(async () => {
    const state = await getAllAuthStatuses();
    setAuthByProvider(state);
  }, []);

  useEffect(() => {
    refreshAllAuthStatuses();
  }, [refreshAllAuthStatuses]);

  async function refreshAuthStatusForProvider(provider: ConnectableProvider) {
    try {
      const status = await getAuthStatus(provider);
      setAuthByProvider((prev) => ({ ...prev, [provider]: status }));
      return status;
    } catch {
      const fallback = { is_authenticated: false, email: null };
      setAuthByProvider((prev) => ({ ...prev, [provider]: fallback }));
      return fallback;
    }
  }

  async function handleConnect(provider: ConnectableProvider) {
    setLoading((prev) => ({ ...prev, [provider]: true }));
    setError(null);
    try {
      const authUrl = await getAuthUrl(provider);
      window.open(authUrl, "_blank", "width=600,height=700");

      const interval = setInterval(async () => {
        try {
          const status = await refreshAuthStatusForProvider(provider);
          if (status?.is_authenticated) {
            clearInterval(interval);
            setLoading((prev) => ({ ...prev, [provider]: false }));
          }
        } catch {
          // on ignore les erreurs et on réessaie au prochain tick
        }
      }, POLL_INTERVAL_MS);

      setTimeout(() => {
        clearInterval(interval);
        setLoading((prev) => ({ ...prev, [provider]: false }));
      }, POLL_TIMEOUT_MS);
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage =
        apiError?.response?.data?.detail ||
        apiError?.message ||
        `Erreur lors de la connexion à ${PROVIDER_LABELS[provider]}`;
      setError(errorMessage);
      setLoading((prev) => ({ ...prev, [provider]: false }));
    }
  }

  async function handleDisconnect(provider: ConnectableProvider) {
    setLoading((prev) => ({ ...prev, [provider]: true }));
    setError(null);
    try {
      await logout(provider);
      setAuthByProvider((prev) => ({ ...prev, [provider]: { is_authenticated: false, email: null } }));
    } catch {
      setError("Erreur lors de la déconnexion");
    } finally {
      setLoading((prev) => ({ ...prev, [provider]: false }));
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Paramètres</h1>

      {CONNECTABLE_PROVIDERS.map((provider) => (
        <AuthProviderCard
          key={provider}
          provider={provider}
          label={PROVIDER_LABELS[provider]}
          status={authByProvider[provider]}
          loading={loading[provider]}
          onConnect={() => handleConnect(provider)}
          onDisconnect={() => handleDisconnect(provider)}
        />
      ))}

      {error && (
        <p style={{ color: colors.error, marginTop: spacing.page }}>{error}</p>
      )}
    </div>
  );
}
