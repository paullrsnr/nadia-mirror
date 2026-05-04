import { useState, useCallback } from "react";
import {
  archiveEmail,
  classifyEmail,
  classifyAllEmails,
  getThreadEmails,
  suggestReply,
} from "../../../services/api/emails.api";
import { summarizeEmail, summarizeThread } from "../../../services/api/llm.api";
import { confirmArchive, rejectArchive } from "../../../services/api/autoArchive.api";
import type { Email, MailProvider } from "../../../types";

interface UseEmailActionsOptions {
  provider: MailProvider;
  onEmailUpdate: (emailId: string, patch: Partial<Email>) => void;
  onEmailRemove: (emailId: string) => void;
  onPendingArchiveRemove: (emailId: string) => void;
  onEmailsReload: () => void;
}

export function useEmailActions({
  provider,
  onEmailUpdate,
  onEmailRemove,
  onPendingArchiveRemove,
  onEmailsReload,
}: UseEmailActionsOptions) {
  const [classifying, setClassifying] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [drafting, setDrafting] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [draft, setDraft] = useState<string | null>(null);
  const [threadCount, setThreadCount] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const resetDetail = useCallback(() => {
    setSummary(null);
    setDraft(null);
    setThreadCount(1);
    setError(null);
  }, []);

  const loadThread = useCallback(async (email: Email) => {
    if (!email.thread_id) return;
    try {
      const thread = await getThreadEmails(email.thread_id);
      const ids = new Set(thread.emails.map((e) => e.id));
      setThreadCount(ids.has(email.id) ? thread.count : thread.count + 1);
    } catch {
      // silencieux — le bouton thread sera masqué
    }
  }, []);

  const handleClassify = useCallback(
    async (email: Email) => {
      setClassifying(true);
      setError(null);
      try {
        const result = await classifyEmail(email.id);
        onEmailUpdate(email.id, { category: result.category });
      } catch {
        setError("Erreur lors de la classification. Vérifiez qu'un modèle LLM est chargé.");
      } finally {
        setClassifying(false);
      }
    },
    [onEmailUpdate],
  );

  const handleClassifyAll = useCallback(async () => {
    setClassifying(true);
    setError(null);
    try {
      const result = await classifyAllEmails(20);
      if (result.classified > 0) {
        onEmailsReload();
      }
    } catch {
      setError("Erreur lors de la classification. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setClassifying(false);
    }
  }, [onEmailsReload]);

  const handleSummarize = useCallback(async (email: Email) => {
    setSummarizing(true);
    setSummary(null);
    try {
      const result = await summarizeEmail(
        email.subject ?? "",
        email.body_text ?? "",
        email.from_address.email,
      );
      setSummary(result.summary);
    } catch {
      setSummary("Erreur lors du résumé. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setSummarizing(false);
    }
  }, []);

  const handleSummarizeThread = useCallback(async (email: Email) => {
    if (!email.thread_id) return;
    setSummarizing(true);
    setSummary(null);
    try {
      const thread = await getThreadEmails(email.thread_id);
      const threadMap = new Map(thread.emails.map((e) => [e.id, e]));
      threadMap.set(email.id, email);
      const threadEmails = Array.from(threadMap.values()).sort(
        (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
      );
      const messages = threadEmails.map((e) => ({
        from_address: e.from_address.email,
        body: e.body_text ?? "",
        date: e.date ? new Date(e.date).toLocaleString("fr-FR") : "",
      }));
      const result = await summarizeThread(email.subject ?? "", messages);
      setSummary(result.summary);
    } catch {
      setSummary("Erreur lors du résumé. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setSummarizing(false);
    }
  }, []);

  const handleSuggestReply = useCallback(async (email: Email) => {
    setDrafting(true);
    setDraft(null);
    try {
      const result = await suggestReply(email.id);
      setDraft(
        result.important && result.draft
          ? result.draft
          : "Cet email ne semble pas nécessiter de réponse.",
      );
    } catch {
      setDraft("Erreur lors de la génération du brouillon. Vérifiez qu'un modèle LLM est chargé.");
    } finally {
      setDrafting(false);
    }
  }, []);

  const handleArchive = useCallback(
    async (email: Email) => {
      const archiveProvider = provider === "all" ? (email.provider ?? "gmail") : provider;
      if (archiveProvider === "all") return;
      try {
        await archiveEmail(email.id, archiveProvider as MailProvider);
        onEmailRemove(email.id);
      } catch {
        setError("Erreur lors de l'archivage");
      }
    },
    [provider, onEmailRemove],
  );

  const handleConfirmArchive = useCallback(
    async (email: Email) => {
      await confirmArchive(email.id);
      onEmailRemove(email.id);
    },
    [onEmailRemove],
  );

  const handleRejectArchive = useCallback(
    async (email: Email) => {
      await rejectArchive(email.id);
      onPendingArchiveRemove(email.id);
    },
    [onPendingArchiveRemove],
  );

  return {
    classifying,
    summarizing,
    drafting,
    summary,
    draft,
    threadCount,
    actionError: error,
    resetDetail,
    loadThread,
    handleClassify,
    handleClassifyAll,
    handleSummarize,
    handleSummarizeThread,
    handleSuggestReply,
    handleArchive,
    handleConfirmArchive,
    handleRejectArchive,
  };
}
