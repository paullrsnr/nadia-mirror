import type { Email } from "../../models";
import { API_BASE_URL } from "./config";

export async function getAutoArchiveRules(): Promise<{ rules: string; enabled: boolean }> {
  const response = await fetch(`${API_BASE_URL}/auto-archive/rules`);
  if (!response.ok) throw new Error("Erreur lors de la récupération des règles");
  return response.json();
}

export async function saveAutoArchiveRules(rules: string): Promise<{ rules: string; enabled: boolean }> {
  const response = await fetch(`${API_BASE_URL}/auto-archive/rules`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rules }),
  });
  if (!response.ok) throw new Error("Erreur lors de la sauvegarde des règles");
  return response.json();
}

export async function getPendingArchive(): Promise<{ emails: Email[]; count: number }> {
  const response = await fetch(`${API_BASE_URL}/auto-archive/pending`);
  if (!response.ok) throw new Error("Erreur lors de la récupération des emails en attente");
  return response.json();
}

export async function confirmArchive(emailId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auto-archive/confirm/${emailId}`, { method: "POST" });
  if (!response.ok) throw new Error("Erreur lors de la confirmation");
}

export async function rejectArchive(emailId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auto-archive/reject/${emailId}`, { method: "POST" });
  if (!response.ok) throw new Error("Erreur lors du refus");
}
