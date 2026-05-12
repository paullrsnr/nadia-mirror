import { apiGet, apiPost } from "./client";
import type { Email, EmailListResponse, SyncResponse, Category, MailProvider } from "../../models";

export async function getEmails(maxResults = 50, provider?: MailProvider): Promise<EmailListResponse> {
  const params: Record<string, string> = { max_results: maxResults.toString() };
  if (provider) params.provider = provider;
  return apiGet<EmailListResponse>("/emails", params);
}

export async function archiveEmail(emailId: string, provider?: MailProvider): Promise<void> {
  const params = provider ? `?provider=${provider}` : "";
  await apiPost(`/emails/archive/${emailId}${params}`);
}

export async function classifyEmail(emailId: string): Promise<{ email_id: string; category: string }> {
  return apiPost(`/emails/classify/${emailId}`);
}

export async function classifyAllEmails(limit = 20): Promise<{ classified: number }> {
  return apiPost(`/emails/classify-all?limit=${limit}`);
}

export async function getThreadEmails(threadId: string): Promise<{ emails: Email[]; count: number }> {
  return apiGet(`/emails/thread/${threadId}`);
}

export async function getCategories(): Promise<Category[]> {
  return apiGet("/emails/categories");
}

export async function suggestReply(emailId: string): Promise<{ important: boolean; draft: string | null }> {
  return apiPost(`/emails/suggest-reply/${emailId}`);
}

export async function triggerSync(
  maxResults = 100,
  provider?: MailProvider,
  full = false,
): Promise<{ status: string }> {
  const params = new URLSearchParams({ max_results: maxResults.toString() });
  if (provider) params.set("provider", provider);
  if (full) params.set("full", "true");
  return apiPost(`/emails/sync?${params}`);
}

export async function getSyncStatus(): Promise<{ status: string; last_result?: SyncResponse }> {
  return apiGet("/emails/sync/status");
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
