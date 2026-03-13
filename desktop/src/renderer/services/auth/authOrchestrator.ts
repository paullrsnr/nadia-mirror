/**
 * Orchestrateur d'authentification : point d'entrée unique pour le front.
 * Agrège les sous-services (Gmail, Outlook) et expose une API unifiée
 * pour les pages (Settings, Inbox, etc.).
 */
import type { AuthStatus, AuthStateByProvider, ConnectableProvider } from "../../models";
import * as providerAuth from "./providerAuth";

const CONNECTABLE_PROVIDERS: ConnectableProvider[] = ["gmail", "outlook"];

/** Récupère le statut d'auth pour tous les providers connectables (un seul appel par provider). */
export async function getAllAuthStatuses(): Promise<AuthStateByProvider> {
  const [gmail, outlook] = await Promise.all([
    providerAuth.getAuthStatus("gmail").catch(() => ({ is_authenticated: false, email: null })),
    providerAuth.getAuthStatus("outlook").catch(() => ({ is_authenticated: false, email: null })),
  ]);
  return { gmail, outlook };
}

/** Récupère le statut pour un seul provider. */
export async function getAuthStatus(provider: ConnectableProvider): Promise<AuthStatus> {
  return providerAuth.getAuthStatus(provider);
}

/** Retourne l'URL d'auth pour le provider (ouvrir en popup). */
export async function getAuthUrl(provider: ConnectableProvider): Promise<string> {
  return providerAuth.getAuthUrl(provider);
}

/** Déconnexion pour un provider. */
export async function logout(provider: ConnectableProvider): Promise<void> {
  return providerAuth.logout(provider);
}

export { CONNECTABLE_PROVIDERS };
export type { ConnectableProvider, AuthStateByProvider } from "../../models";
