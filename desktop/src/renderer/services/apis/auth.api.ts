import type { ApiError, AuthStatus, AuthUrl } from "../../models";
import { API_BASE_URL } from "./config";

export type { ApiError, AuthStatus, AuthUrl } from "../../models";

export type MailProvider = "gmail" | "outlook" | "all";

export async function getAuthUrl(provider?: MailProvider): Promise<string> {
  const params = provider ? `?provider=${provider}` : "";
  const response = await fetch(`${API_BASE_URL}/auth/url${params}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error: ApiError = Object.assign(
      new Error(errorData.detail || "Erreur lors de la récupération de l'URL d'authentification"),
      { response: { data: errorData } }
    );
    throw error;
  }

  const data: AuthUrl = await response.json();
  return data.auth_url;
}

export async function getAuthStatus(provider?: MailProvider): Promise<AuthStatus> {
  const params = provider ? `?provider=${provider}` : "";
  const response = await fetch(`${API_BASE_URL}/auth/status${params}`);

  if (!response.ok) {
    throw new Error("Erreur lors de la vérification du statut d'authentification");
  }

  const data: AuthStatus = await response.json();
  return data;
}

export async function logout(provider?: MailProvider): Promise<void> {
  const params = provider ? `?provider=${provider}` : "";
  const response = await fetch(`${API_BASE_URL}/auth/logout${params}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la déconnexion");
  }
}
