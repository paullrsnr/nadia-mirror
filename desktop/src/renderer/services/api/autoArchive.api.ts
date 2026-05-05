import { apiGet, apiPost } from "./client";
import type { Email } from "../../types";

export async function getAutoArchiveRules(): Promise<{ rules: string; enabled: boolean }> {
  return apiGet("/auto-archive/rules");
}

export async function saveAutoArchiveRules(rules: string): Promise<{ rules: string; enabled: boolean }> {
  return apiPost("/auto-archive/rules", { rules });
}

export async function getPendingArchive(): Promise<{ emails: Email[]; count: number }> {
  return apiGet("/auto-archive/pending");
}

export async function confirmArchive(emailId: string): Promise<void> {
  await apiPost(`/auto-archive/confirm/${emailId}`);
}

export async function rejectArchive(emailId: string): Promise<void> {
  await apiPost(`/auto-archive/reject/${emailId}`);
}
