import { useState, useEffect, useCallback } from "react";
import type { ApiError } from "../services/apis/auth.api";
import AuthProviderCard from "../components/AuthProviderCard";
import { getAutoArchiveRules, saveAutoArchiveRules } from "../services/apis/autoArchive.api";
import { colors, spacing, radius } from "../theme";
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
  const [archiveRules, setArchiveRules] = useState("");
  const [archiveRulesSaved, setArchiveRulesSaved] = useState(false);

  useEffect(() => {
    getAutoArchiveRules().then((data) => setArchiveRules(data.rules)).catch(() => {});
  }, []);

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
      setAuthByProvider((prev: AuthStateByProvider) => ({ ...prev, [provider]: status }));
      return status;
    } catch {
      const fallback = { is_authenticated: false, email: null };
      setAuthByProvider((prev: AuthStateByProvider) => ({ ...prev, [provider]: fallback }));
      return fallback;
    }
  }

  async function handleConnect(provider: ConnectableProvider) {
    setLoading((prev: Record<ConnectableProvider, boolean>) => ({ ...prev, [provider]: true }));
    setError(null);
    try {
      const authUrl = await getAuthUrl(provider);
      window.open(authUrl, "_blank", "width=600,height=700");

      const interval = setInterval(async () => {
        try {
          const status = await refreshAuthStatusForProvider(provider);
          if (status?.is_authenticated) {
            clearInterval(interval);
            setLoading((prev: Record<ConnectableProvider, boolean>) => ({ ...prev, [provider]: false }));
          }
        } catch {
          // on ignore les erreurs et on réessaie au prochain tick
        }
      }, POLL_INTERVAL_MS);

      setTimeout(() => {
        clearInterval(interval);
        setLoading((prev: Record<ConnectableProvider, boolean>) => ({ ...prev, [provider]: false }));
      }, POLL_TIMEOUT_MS);
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage =
        apiError?.response?.data?.detail ||
        apiError?.message ||
        `Erreur lors de la connexion à ${PROVIDER_LABELS[provider]}`;
      setError(errorMessage);
      setLoading((prev: Record<ConnectableProvider, boolean>) => ({ ...prev, [provider]: false }));
    }
  }

  async function handleDisconnect(provider: ConnectableProvider) {
    setLoading((prev: Record<ConnectableProvider, boolean>) => ({ ...prev, [provider]: true }));
    setError(null);
    try {
      await logout(provider);
      setAuthByProvider((prev: AuthStateByProvider) => ({ ...prev, [provider]: { is_authenticated: false, email: null } }));
    } catch {
      setError("Erreur lors de la déconnexion");
    } finally {
      setLoading((prev: Record<ConnectableProvider, boolean>) => ({ ...prev, [provider]: false }));
    }
  }

  async function handleSaveArchiveRules() {
    await saveAutoArchiveRules(archiveRules);
    setArchiveRulesSaved(true);
    setTimeout(() => setArchiveRulesSaved(false), 2000);
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

      <div style={{ marginTop: spacing.page, padding: spacing.page, border: `1px solid ${colors.borderStrong}`, borderRadius: radius.sm }}>
        <h2 style={{ margin: `0 0 ${spacing.sm}px` }}>Archivage automatique (IA)</h2>
        <p style={{ margin: `0 0 ${spacing.sm}px`, color: colors.textSecondary, fontSize: "13px" }}>
          Décrivez les emails à archiver automatiquement. L'IA archivera directement les emails correspondants et vous demandera confirmation pour les cas incertains.
        </p>
        <p style={{ margin: `0 0 ${spacing.sm}px`, color: colors.textMuted, fontSize: "12px" }}>
          Exemples : "emails marketing et newsletters", "promotions Amazon et Spotify", "notifications automatiques sans action requise"
        </p>
        <textarea
          value={archiveRules}
          onChange={(e) => setArchiveRules(e.target.value)}
          placeholder="Ex : Archiver les newsletters, les emails promotionnels, et les notifications automatiques des réseaux sociaux."
          rows={4}
          style={{ width: "100%", padding: spacing.sm, borderRadius: radius.sm, border: `1px solid ${colors.borderStrong}`, backgroundColor: colors.backgroundMuted, color: colors.textPrimary, fontSize: "13px", resize: "vertical", boxSizing: "border-box" }}
        />
        <button
          onClick={handleSaveArchiveRules}
          style={{ marginTop: spacing.sm, padding: `${spacing.sm}px 16px`, backgroundColor: colors.buttonPrimary, color: colors.background, border: "none", borderRadius: radius.sm, cursor: "pointer" }}
        >
          {archiveRulesSaved ? "Enregistré ✓" : "Enregistrer les règles"}
        </button>
      </div>

      {error && (
        <p style={{ color: colors.error, marginTop: spacing.page }}>{error}</p>
      )}
    </div>
  );
}
