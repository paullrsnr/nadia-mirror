import type { ConnectableProvider } from "./ConnectableProvider";
import type { AuthStateByProvider } from "./AuthStateByProvider";

export interface UseAuthResult {
  authByProvider: AuthStateByProvider;
  loading: Record<ConnectableProvider, boolean>;
  error: string | null;
  providers: ConnectableProvider[];
  connect: (provider: ConnectableProvider) => Promise<void>;
  disconnect: (provider: ConnectableProvider) => Promise<void>;
}
