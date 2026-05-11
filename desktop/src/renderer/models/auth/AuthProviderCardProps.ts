import type { AuthStatus } from "./AuthStatus";
import type { ConnectableProvider } from "./ConnectableProvider";

export interface AuthProviderCardProps {
  readonly provider: ConnectableProvider;
  readonly label: string;
  readonly status: AuthStatus | null;
  readonly loading: boolean;
  readonly onConnect: () => void;
  readonly onDisconnect: () => void;
  readonly children?: React.ReactNode;
}