import { useState, useCallback } from "react";
import { triggerSync, waitForSync } from "../../../services/api/emails.api";
import type { MailProvider, UseSyncResult } from "../../../types";

export function useSync(provider: MailProvider, onSyncComplete: () => void): UseSyncResult {
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sync = useCallback(
    async (full = false) => {
      setSyncing(true);
      setError(null);
      try {
        await triggerSync(100, provider, full);
        waitForSync(
          () => {
            onSyncComplete();
            setSyncing(false);
          },
          (msg) => {
            setError(msg);
            setSyncing(false);
          },
        );
      } catch {
        setError("Erreur lors de la synchronisation");
        setSyncing(false);
      }
    },
    [provider, onSyncComplete],
  );

  return { syncing, syncError: error, sync };
}
