import type { AuthStatus } from "./AuthStatus";

export interface AuthStateByProvider {
  gmail: AuthStatus | null;
  outlook: AuthStatus | null;
}
