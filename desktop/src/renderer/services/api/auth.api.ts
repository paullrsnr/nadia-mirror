import { apiGet, apiPost } from "./client";
import type { AuthStatus, AuthUrl, ConnectableProvider, MailProvider, ApiError } from "../../types";

export type { ConnectableProvider, MailProvider, ApiError };

export const CONNECTABLE_PROVIDERS: ConnectableProvider[] = ["gmail", "outlook"];

function resolveProvider(provider?: MailProvider): string {
  return provider && provider !== "all" ? provider : "gmail";
}

export async function getAuthUrl(provider: ConnectableProvider): Promise<string> {
  try {
    const data = await apiGet<AuthUrl>(`/auth/url/${provider}`);
    return data.auth_url;
  } catch (err) {
    const error: ApiError = Object.assign(
      new Error((err as Error).message || "Erreur lors de la récupération de l'URL d'authentification"),
      { response: { data: { detail: (err as Error).message } } }
    );
    throw error;
  }
}

export async function getAuthStatus(provider?: MailProvider): Promise<AuthStatus> {
  return apiGet<AuthStatus>(`/auth/status/${resolveProvider(provider)}`);
}

export async function getAllAuthStatuses(): Promise<{ gmail: AuthStatus; outlook: AuthStatus }> {
  const [gmail, outlook] = await Promise.all([
    getAuthStatus("gmail").catch(() => ({ is_authenticated: false, email: null })),
    getAuthStatus("outlook").catch(() => ({ is_authenticated: false, email: null })),
  ]);
  return { gmail, outlook };
}

export async function logout(provider?: MailProvider): Promise<void> {
  await apiPost(`/auth/logout/${resolveProvider(provider)}`);
}
