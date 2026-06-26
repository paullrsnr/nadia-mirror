import { useState, useEffect, useCallback } from "react";
import { useComputed } from "@preact/signals-react";
import { getEmails, getCategories } from "../../../services/api/emails.api";
import { getAllAuthStatuses } from "../../../services/api/auth.api";
import { getPendingArchive } from "../../../services/api/autoArchive.api";
import { authSignal } from "../../../state";
import { UNREAD_LABEL } from "../../../constants/labels";
import type { Email, Category, MailProvider, InboxFolder, UseEmailsResult } from "../../../models";

export function useEmails(provider: MailProvider, folder: InboxFolder = "inbox"): UseEmailsResult {
  const fetchFolder = folder === "sent" ? "sent" : "inbox";
  const [emails, setEmails] = useState<Email[]>([]);
  const [pendingArchive, setPendingArchive] = useState<Email[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = useComputed(() => {
    const statuses = authSignal.value;
    const authenticated =
      provider === "all"
        ? statuses.gmail?.is_authenticated || statuses.outlook?.is_authenticated
        : statuses[provider]?.is_authenticated;
    return authenticated ?? false;
  }).value;

  const loadEmails = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getEmails(50, provider, fetchFolder);
      setEmails(response.emails);
    } catch {
      setError("Erreur lors du chargement des emails");
    } finally {
      setLoading(false);
    }
  }, [provider, fetchFolder]);

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

        const labels = new Set(e.labels);
        if (read) labels.delete(UNREAD_LABEL);
        else labels.add(UNREAD_LABEL);

        return { ...e, labels: [...labels] };
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
