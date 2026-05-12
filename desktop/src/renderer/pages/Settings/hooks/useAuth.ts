import { useState, useEffect, useCallback } from "react";
import { useComputed } from "@preact/signals-react";
import {
  getAllAuthStatuses,
  getAuthStatus,
  getAuthUrl,
  logout,
  CONNECTABLE_PROVIDERS,
} from "../../../services/api/auth.api";
import { authSignal } from "../../../state";
import type { ConnectableProvider, ApiError, UseAuthResult } from "../../../models";

const POLL_INTERVAL_MS = 2000;
const POLL_TIMEOUT_MS = 300_000;

export function useAuth(): UseAuthResult {
  const authByProviderComputed = useComputed(() => authSignal.value);
  const authByProvider = authByProviderComputed.value;
  const [loading, setLoading] = useState<Record<ConnectableProvider, boolean>>({
    gmail: false,
    outlook: false,
  });
  const [error, setError] = useState<string | null>(null);

  const setProviderLoading = useCallback((provider: ConnectableProvider, value: boolean) => {
    setLoading((prev) => ({ ...prev, [provider]: value }));
  }, []);

  const refreshAll = useCallback(async () => {
    const state = await getAllAuthStatuses();
    authSignal.value = state;
  }, []);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const connect = useCallback(
    async (provider: ConnectableProvider) => {
      setProviderLoading(provider, true);
      setError(null);
      try {
        const authUrl = await getAuthUrl(provider);
        window.open(authUrl, "_blank", "width=600,height=700");

        const interval = setInterval(async () => {
          try {
            const status = await getAuthStatus(provider);
            authSignal.value = { ...authSignal.value, [provider]: status };
            if (status.is_authenticated) {
              clearInterval(interval);
              setProviderLoading(provider, false);
            }
          } catch {
            // réessai au prochain tick
          }
        }, POLL_INTERVAL_MS);

        setTimeout(() => {
          clearInterval(interval);
          setProviderLoading(provider, false);
        }, POLL_TIMEOUT_MS);
      } catch (err) {
        const apiError = err as ApiError;
        setError(
          apiError?.response?.data?.detail ||
            apiError?.message ||
            `Erreur lors de la connexion à ${provider}`,
        );
        setProviderLoading(provider, false);
      }
    },
    [setProviderLoading],
  );

  const disconnect = useCallback(
    async (provider: ConnectableProvider) => {
      setProviderLoading(provider, true);
      setError(null);
      try {
        await logout(provider);
        authSignal.value = {
          ...authSignal.value,
          [provider]: { is_authenticated: false, email: null },
        };
      } catch {
        setError("Erreur lors de la déconnexion");
      } finally {
        setProviderLoading(provider, false);
      }
    },
    [setProviderLoading],
  );

  return {
    authByProvider,
    loading,
    error,
    providers: CONNECTABLE_PROVIDERS,
    connect,
    disconnect,
  };
}
