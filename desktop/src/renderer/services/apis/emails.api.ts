import type { Email, EmailListResponse, SyncResponse } from "../../models";
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

export async function classifyEmail(emailId: string): Promise<{ email_id: string; category: string }> {
  const response = await fetch(`${API_BASE_URL}/emails/classify/${emailId}`, { method: "POST" });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erreur inconnue" }));
    throw new Error(error.detail || "Erreur lors de la classification");
  }
  return response.json();
}

export async function classifyAllEmails(limit = 20): Promise<{ classified: number }> {
  const response = await fetch(`${API_BASE_URL}/emails/classify-all?limit=${limit}`, { method: "POST" });
  if (!response.ok) {
    throw new Error("Erreur lors de la classification");
  }
  return response.json();
}

export async function getThreadEmails(threadId: string): Promise<{ emails: Email[]; count: number }> {
  const response = await fetch(`${API_BASE_URL}/emails/thread/${threadId}`);
  if (!response.ok) {
    throw new Error("Erreur lors de la récupération du fil de discussion");
  }
  return response.json();
}

export async function getCategories(): Promise<{ id: number; name: string }[]> {
  const response = await fetch(`${API_BASE_URL}/emails/categories`);
  if (!response.ok) throw new Error("Erreur lors de la récupération des catégories");
  return response.json();
}

export async function suggestReply(emailId: string): Promise<{ important: boolean; draft: string | null }> {
  const response = await fetch(`${API_BASE_URL}/emails/suggest-reply/${emailId}`, { method: "POST" });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erreur inconnue" }));
    throw new Error(error.detail || "Erreur lors de la génération du brouillon");
  }
  return response.json();
}

export async function triggerSync(
  maxResults: number = 100,
  provider?: MailProvider,
): Promise<{ status: string }> {
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

export async function getSyncStatus(): Promise<{ status: string; last_result?: SyncResponse }> {
  const response = await fetch(`${API_BASE_URL}/emails/sync/status`);
  if (!response.ok) {
    throw new Error("Erreur lors de la récupération du statut");
  }
  return response.json();
}

export async function waitForSync(
  onComplete: () => void,
  onError: (msg: string) => void,
  intervalMs = 2000,
): Promise<void> {
  const poll = async () => {
    try {
      const { status, last_result } = await getSyncStatus();
      if (status === "idle") {
        if (last_result?.status === "error") {
          onError(last_result.message ?? "Erreur lors de la synchronisation");
        } else {
          onComplete();
        }
        return;
      }
      setTimeout(poll, intervalMs);
    } catch {
      onError("Erreur lors de la synchronisation");
    }
  };
  setTimeout(poll, intervalMs);
}
