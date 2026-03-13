import { AuthStatus } from "./AuthStatus";

/** Providers pour lesquels on peut se connecter (exclut "all") */
export type ConnectableProvider = "gmail" | "outlook";

export interface AuthStateByProvider {
  gmail: AuthStatus | null;
  outlook: AuthStatus | null;
}
