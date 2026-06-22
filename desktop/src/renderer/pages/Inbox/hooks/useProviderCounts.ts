import { useCallback, useEffect, useState } from "react";
import { useComputed } from "@preact/signals-react";
import { getEmails } from "../../../services/api/emails.api";
import { authSignal } from "../../../state";
import type { ConnectableProvider, ProviderCount, UseProviderCountsResult } from "../../../models";

const PROVIDERS: ConnectableProvider[] = ["gmail", "outlook"];

export function useProviderCounts(): UseProviderCountsResult {
  const authByProvider = useComputed(() => authSignal.value).value;
  const [providerCounts, setProviderCounts] = useState<
    Partial<Record<ConnectableProvider, ProviderCount>>
  >({});

  const connectedProviders = PROVIDERS.filter((p) => authByProvider[p]?.is_authenticated);
  const connectedKey = connectedProviders.join(",");

  const refreshProviderCounts = useCallback(() => {
    connectedProviders.forEach((provider) => {
      getEmails(50, provider)
        .then((response) => {
          const unread = response.emails.filter((e) => e.labels.includes("UNREAD")).length;
          const starred = response.emails.filter((e) => e.is_starred).length;
          setProviderCounts((prev) => ({
            ...prev,
            [provider]: { total: response.total, unread, starred },
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
