import type { ApiError, AuthStatus, AuthUrl } from "../../models";
import { API_BASE_URL } from "./config";

export type { ApiError, AuthStatus, AuthUrl } from "../../models";

export async function getAuthUrl(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/url`);

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

export async function getAuthStatus(): Promise<AuthStatus> {
  const response = await fetch(`${API_BASE_URL}/auth/status`);

  if (!response.ok) {
    throw new Error("Erreur lors de la vérification du statut d'authentification");
  }

  const data: AuthStatus = await response.json();
  return data;
}

export async function logout(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la déconnexion");
  }
}
