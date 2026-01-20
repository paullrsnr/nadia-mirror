const API_BASE_URL = "http://127.0.0.1:3333";

export interface AuthStatus {
  is_authenticated: boolean;
  email: string | null;
}

export interface AuthUrl {
  auth_url: string;
}

export async function getAuthUrl(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/url`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(errorData.detail || "Erreur lors de la récupération de l'URL d'authentification");
    (error as any).response = { data: errorData };
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

export async function authCallback(code: string, state?: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auth/callback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code, state }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur lors de l'authentification");
  }
}

export async function logout(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la déconnexion");
  }
}
