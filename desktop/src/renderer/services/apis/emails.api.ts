import type { EmailListResponse, SyncResponse } from "../../models";
import type { MailProvider } from "./auth.api";
import { API_BASE_URL } from "./config";

export type { Email, EmailListResponse, SyncResponse } from "../../models";

export async function getEmails(
  maxResults: number = 50,
  provider?: MailProvider,
): Promise<EmailListResponse> {
  const params = new URLSearchParams({ max_results: maxResults.toString() });
  if (provider) params.set("provider", provider);
  const response = await fetch(`${API_BASE_URL}/emails?${params}`);

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération des emails");
  }

  return response.json();
}

export async function archiveEmail(emailId: string, provider?: MailProvider): Promise<void> {
  const params = provider ? `?provider=${provider}` : "";
  const response = await fetch(`${API_BASE_URL}/emails/archive/${emailId}${params}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de l'archivage");
  }
}

export async function syncEmails(
  maxResults: number = 100,
  provider?: MailProvider,
): Promise<SyncResponse> {
  const params = new URLSearchParams({ max_results: maxResults.toString() });
  if (provider) params.set("provider", provider);
  const response = await fetch(`${API_BASE_URL}/emails/sync?${params}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la synchronisation");
  }

  return response.json();
}
