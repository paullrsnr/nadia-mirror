/**
 * Sous-services d'auth par provider : un point d'entrée par source (Gmail, Outlook, etc.).
 * L'orchestrateur les utilise pour éviter de mélanger la logique dans les pages.
 */
import type { AuthStatus, ConnectableProvider } from "../../models";
import * as authApi from "../apis/auth.api";

export async function getAuthUrl(provider: ConnectableProvider): Promise<string> {
  return authApi.getAuthUrl(provider);
}

export async function getAuthStatus(provider: ConnectableProvider): Promise<AuthStatus> {
  return authApi.getAuthStatus(provider);
}

export async function logout(provider: ConnectableProvider): Promise<void> {
  return authApi.logout(provider);
}
