import { useState, useEffect, useCallback } from "react";
import { getEmails, getCategories } from "../../../services/api/emails.api";
import { getAuthStatus } from "../../../services/api/auth.api";
import { getPendingArchive } from "../../../services/api/autoArchive.api";
import type { Email, Category, MailProvider, UseEmailsResult } from "../../../models";

export function useEmails(provider: MailProvider): UseEmailsResult {
  const [emails, setEmails] = useState<Email[]>([]);
  const [pendingArchive, setPendingArchive] = useState<Email[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const loadEmails = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getEmails(50, provider);
      setEmails(response.emails);
    } catch {
      setError("Erreur lors du chargement des emails");
    } finally {
      setLoading(false);
    }
  }, [provider]);

  const loadPendingArchive = useCallback(async () => {
    try {
      const pending = await getPendingArchive();
      setPendingArchive(pending.emails);
    } catch {
      // silencieux
    }
  }, []);

  const loadAll = useCallback(async () => {
    await Promise.all([loadEmails(), loadPendingArchive()]);
  }, [loadEmails, loadPendingArchive]);

  const initialize = useCallback(async () => {
    try {
      const authStatus = await getAuthStatus(provider);
      setIsAuthenticated(authStatus.is_authenticated);
      if (authStatus.is_authenticated) await loadAll();
    } catch {
      setError("Erreur de connexion");
    }
  }, [provider, loadAll]);

  useEffect(() => {
    setEmails([]);
    setIsAuthenticated(false);
    setError(null);
    initialize();
  }, [initialize]);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
  }, []);

  const removeEmail = useCallback((emailId: string) => {
    setEmails((prev) => prev.filter((e) => e.id !== emailId));
    setPendingArchive((prev) => prev.filter((e) => e.id !== emailId));
  }, []);

  const removePendingArchive = useCallback((emailId: string) => {
    setPendingArchive((prev) => prev.filter((e) => e.id !== emailId));
  }, []);

  return {
    emails,
    pendingArchive,
    categories,
    loading,
    error,
    isAuthenticated,
    loadEmails,
    loadAll,
    removeEmail,
    removePendingArchive,
  };
}
