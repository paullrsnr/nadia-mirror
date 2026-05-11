import { useState, useEffect, useCallback } from "react";
import { getEmails, getCategories } from "../../../services/api/emails.api";
import { getAuthStatus } from "../../../services/api/auth.api";
import { getPendingArchive } from "../../../services/api/autoArchive.api";
import type { Email, Category, MailProvider, UseEmailsResult } from "../../../models";

interface UseEmailsState {
  emails: Email[];
  pendingArchive: Email[];
  categories: Category[];
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

export function useEmails(provider: MailProvider): UseEmailsResult {
  const [state, setState] = useState<UseEmailsState>({
    emails: [],
    pendingArchive: [],
    categories: [],
    loading: false,
    error: null,
    isAuthenticated: false,
  });

  const loadEmails = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const response = await getEmails(50, provider);
      setState((s) => ({ ...s, emails: response.emails, loading: false }));
    } catch {
      setState((s) => ({ ...s, error: "Erreur lors du chargement des emails", loading: false }));
    }
  }, [provider]);

  const loadPendingArchive = useCallback(async () => {
    try {
      const pending = await getPendingArchive();
      setState((s) => ({ ...s, pendingArchive: pending.emails }));
    } catch {
      // silencieux
    }
  }, []);

  const initialize = useCallback(async () => {
    try {
      const authStatus = await getAuthStatus(provider);
      setState((s) => ({ ...s, isAuthenticated: authStatus.is_authenticated }));
      if (authStatus.is_authenticated) {
        await loadEmails();
        await loadPendingArchive();
      }
    } catch {
      setState((s) => ({ ...s, error: "Erreur de connexion" }));
    }
  }, [provider, loadEmails, loadPendingArchive]);

  useEffect(() => {
    setState((s) => ({
      ...s,
      emails: [],
      isAuthenticated: false,
      error: null,
    }));
    initialize();
  }, [initialize]);

  useEffect(() => {
    getCategories()
      .then((cats) => setState((s) => ({ ...s, categories: cats })))
      .catch(() => {});
  }, []);

  const updateEmail = useCallback((emailId: string, patch: Partial<Email>) => {
    setState((s) => ({
      ...s,
      emails: s.emails.map((e) => (e.id === emailId ? { ...e, ...patch } : e)),
    }));
  }, []);

  const removeEmail = useCallback((emailId: string) => {
    setState((s) => ({
      ...s,
      emails: s.emails.filter((e) => e.id !== emailId),
      pendingArchive: s.pendingArchive.filter((e) => e.id !== emailId),
    }));
  }, []);

  const removePendingArchive = useCallback((emailId: string) => {
    setState((s) => ({
      ...s,
      pendingArchive: s.pendingArchive.filter((e) => e.id !== emailId),
    }));
  }, []);

  return {
    ...state,
    loadEmails,
    loadPendingArchive,
    updateEmail,
    removeEmail,
    removePendingArchive,
  };
}
