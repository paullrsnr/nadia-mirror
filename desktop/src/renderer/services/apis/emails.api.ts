import type { EmailListResponse, SyncResponse } from "../../models";
import { API_BASE_URL } from "./config";

export type { Email, EmailListResponse, SyncResponse } from "../../models";

export async function getEmails(maxResults: number = 50): Promise<EmailListResponse> {
  const params = new URLSearchParams({ max_results: maxResults.toString() });
  const response = await fetch(`${API_BASE_URL}/emails?${params}`);

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération des emails");
  }

  return response.json();
}

export async function archiveEmail(emailId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/emails/${emailId}/archive`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de l'archivage");
  }
}

export async function syncEmails(maxResults: number = 100): Promise<SyncResponse> {
  const params = new URLSearchParams({ max_results: maxResults.toString() });
  const response = await fetch(`${API_BASE_URL}/emails/sync?${params}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la synchronisation");
  }

  return response.json();
}
