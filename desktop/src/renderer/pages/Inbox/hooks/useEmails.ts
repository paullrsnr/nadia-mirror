import { useState, useEffect, useCallback } from "react";
import { useComputed } from "@preact/signals-react";
import { getEmails, getCategories } from "../../../services/api/emails.api";
import { getAllAuthStatuses } from "../../../services/api/auth.api";
import { getPendingArchive } from "../../../services/api/autoArchive.api";
import { authSignal } from "../../../state";
import { UNREAD_LABEL } from "../../../constants/labels";
import type { Email, Category, MailProvider, UseEmailsResult } from "../../../models";

export function useEmails(provider: MailProvider): UseEmailsResult {
  const [emails, setEmails] = useState<Email[]>([]);
  const [pendingArchive, setPendingArchive] = useState<Email[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = useComputed(() => {
    const statuses = authSignal.value;
    return provider === "all"
      ? statuses.gmail?.is_authenticated === true || statuses.outlook?.is_authenticated === true
      : statuses[provider]?.is_authenticated === true;
  }).value;

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

  useEffect(() => {
    getAllAuthStatuses()
      .then((statuses) => (authSignal.value = statuses))
      .catch(() => setError("Erreur de connexion"));
  }, []);

  useEffect(() => {
    setEmails([]);
    if (isAuthenticated) loadAll();
  }, [provider, isAuthenticated, loadAll]);

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

  const setEmailStarred = useCallback((emailId: string, starred: boolean) => {
    setEmails((prev) => prev.map((e) => (e.id === emailId ? { ...e, is_starred: starred } : e)));
  }, []);

  const setEmailRead = useCallback((emailId: string, read: boolean) => {
    setEmails((prev) =>
      prev.map((e) => {
        if (e.id !== emailId) return e;
        const labels = read
          ? e.labels.filter((l) => l !== UNREAD_LABEL)
          : e.labels.includes(UNREAD_LABEL)
            ? e.labels
            : [...e.labels, UNREAD_LABEL];
        return { ...e, labels };
      }),
    );
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
    setEmailStarred,
    setEmailRead,
  };
}
