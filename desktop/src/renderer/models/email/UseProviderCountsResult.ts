import type { ProviderCount } from "./ProviderCount";
import type { ConnectableProvider } from "../auth/ConnectableProvider";

export interface UseProviderCountsResult {
  providerCounts: Partial<Record<ConnectableProvider, ProviderCount>>;
  refreshProviderCounts: () => void;
}
