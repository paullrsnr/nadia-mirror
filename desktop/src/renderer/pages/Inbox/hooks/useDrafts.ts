import { useCallback, useState } from "react";
import { listDrafts } from "../../../services/api/drafts.api";
import type { DraftEmail, MailProvider, UseDraftsResult } from "../../../models";

export function useDrafts(provider: MailProvider): UseDraftsResult {
  const [drafts, setDrafts] = useState<DraftEmail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDrafts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await listDrafts(provider === "all" ? undefined : provider);
      setDrafts(result);
    } catch {
      setError("Erreur lors du chargement des brouillons");
    } finally {
      setLoading(false);
    }
  }, [provider]);

  const removeDraft = useCallback((draftId: string) => {
    setDrafts((prev) => prev.filter((d) => d.id !== draftId));
  }, []);

  return { drafts, loading, error, loadDrafts, removeDraft };
}
