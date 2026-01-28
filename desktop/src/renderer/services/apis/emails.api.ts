import { API_BASE_URL } from "./config";

export interface Email {
  id: string;
  thread_id: string;
  subject: string;
  from_address: { name: string | null; email: string };
  to_addresses: Array<{ name: string | null; email: string }>;
  cc_addresses: Array<{ name: string | null; email: string }>;
  date: string;
  body_text: string;
  body_html?: string;
  attachments: Array<{
    filename: string;
    mime_type: string;
    size: number;
    attachment_id: string;
  }>;
  labels: string[];
  snippet?: string;
}

// EmailThread - À implémenter

export interface EmailListResponse {
  emails: Email[];
  total: number;
  page: number;
  page_size: number;
}

export async function getEmails(
  maxResults: number = 50,
  query?: string,
  pageToken?: string
): Promise<EmailListResponse> {
  const params = new URLSearchParams({
    max_results: maxResults.toString(),
  });
  if (query) params.append("query", query);
  if (pageToken) params.append("page_token", pageToken);

  const response = await fetch(`${API_BASE_URL}/emails?${params}`);

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération des emails");
  }

  return response.json();
}

// getEmail - À implémenter

// getThreads - À implémenter

// getThread - À implémenter

export async function archiveEmail(emailId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/emails/${emailId}/archive`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de l'archivage");
  }
}

// markAsRead - À implémenter

export interface SyncResponse {
  status: "success" | "error";
  synced?: number;
  saved?: number;
  timestamp?: string;
  message?: string;
}

export async function syncEmails(
  maxResults: number = 100,
  force: boolean = false
): Promise<SyncResponse> {
  const params = new URLSearchParams({
    max_results: maxResults.toString(),
    force: force.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/emails/sync?${params}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la synchronisation");
  }

  return response.json();
}
