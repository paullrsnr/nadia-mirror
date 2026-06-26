import { apiGet, apiPost, apiPostForm, apiDelete } from "./client";
import type { DraftEmail, DraftPayload, EmailAttachment, MailProvider } from "../../models";

export async function listDrafts(provider?: MailProvider): Promise<DraftEmail[]> {
  const params: Record<string, string> = {};
  if (provider) params.provider = provider;
  return apiGet<DraftEmail[]>("/drafts", params);
}

export async function saveDraft(draftId: string, payload: DraftPayload): Promise<unknown> {
  return apiPost(`/drafts/${draftId}`, payload);
}

export async function sendDraft(draftId: string): Promise<{ status: string; draft_id: string }> {
  return apiPost(`/drafts/${draftId}/send`);
}

export async function deleteDraft(draftId: string): Promise<void> {
  await apiDelete(`/drafts/${draftId}`);
}

export async function uploadAttachment(draftId: string, file: File): Promise<EmailAttachment> {
  const formData = new FormData();
  formData.append("file", file);
  return apiPostForm<EmailAttachment>(`/drafts/${draftId}/attachments`, formData);
}

export async function deleteAttachment(draftId: string, attachmentId: string): Promise<void> {
  await apiDelete(`/drafts/${draftId}/attachments/${attachmentId}`);
}
