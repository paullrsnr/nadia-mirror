import { useCallback, useEffect, useState } from "react";
import { useComputed } from "@preact/signals-react";
import { getEmails } from "../../../services/api/emails.api";
import { listDrafts } from "../../../services/api/drafts.api";
import { authSignal } from "../../../state";
import { CONNECTABLE_PROVIDERS } from "../../../constants/providers";
import { UNREAD_LABEL } from "../../../constants/labels";
import type { ConnectableProvider, ProviderCount, UseProviderCountsResult } from "../../../models";

export function useProviderCounts(): UseProviderCountsResult {
  const authByProvider = useComputed(() => authSignal.value).value;
  const [providerCounts, setProviderCounts] = useState<
    Partial<Record<ConnectableProvider, ProviderCount>>
  >({});

  const connectedProviders = CONNECTABLE_PROVIDERS.filter((p) => authByProvider[p]?.is_authenticated);
  const connectedKey = connectedProviders.join(",");

  const refreshProviderCounts = useCallback(() => {
    connectedProviders.forEach((provider) => {
      getEmails(50, provider)
        .then((response) => {
          const totalUnread = response.emails.filter((e) => e.labels.includes(UNREAD_LABEL)).length;
          const totalStarred = response.emails.filter((e) => e.is_starred).length;
          setProviderCounts((prev) => ({
            ...prev,
            [provider]: { ...prev[provider], total: response.total, totalUnread, totalStarred },
          }));
        })
        .catch(() => {});
      listDrafts(provider)
        .then((drafts) => {
          setProviderCounts((prev) => ({
            ...prev,
            [provider]: {
              total: 0,
              unread: 0,
              starred: 0,
              ...prev[provider],
              drafts: drafts.length,
            },
          }));
        })
        .catch(() => {});
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connectedKey]);

  useEffect(() => {
    refreshProviderCounts();
  }, [refreshProviderCounts]);

  return { providerCounts, refreshProviderCounts };
}
