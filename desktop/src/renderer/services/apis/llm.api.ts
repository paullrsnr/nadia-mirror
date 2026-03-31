import type { LlmStatus } from "../../models/LlmStatus";
import type { CatalogModel } from "../../models/CatalogModel";
import { API_BASE_URL } from "./config";

export type { LlmStatus, CatalogModel };

export async function getLlmStatus(): Promise<LlmStatus> {
  const response = await fetch(`${API_BASE_URL}/llm/status`);
  if (!response.ok) {
    throw new Error("Erreur lors de la récupération du statut LLM");
  }
  return response.json();
}

export async function getCatalog(): Promise<CatalogModel[]> {
  const response = await fetch(`${API_BASE_URL}/llm/models/catalog`);
  if (!response.ok) {
    throw new Error("Erreur lors de la récupération du catalogue");
  }
  return response.json();
}

export interface SummarizeResponse {
  summary: string;
}

export async function summarizeEmail(
  subject: string,
  body: string,
  fromAddress: string = ""
): Promise<SummarizeResponse> {
  const response = await fetch(`${API_BASE_URL}/llm/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject, body, from_address: fromAddress }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erreur inconnue" }));
    throw new Error(error.detail || "Erreur lors du résumé");
  }
  return response.json();
}

export interface DownloadProgress {
  status: "starting" | "progress" | "completed" | "exists" | "error";
  repo?: string;
  filename?: string;
  path?: string;
  progress?: number;
  error?: string;
}

export async function downloadModel(
  repo: string,
  filename: string,
  onProgress: (progress: DownloadProgress) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/llm/models/download/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo, filename }),
  });

  if (!response.ok) {
    throw new Error("Erreur lors du téléchargement");
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Stream non disponible");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6)) as DownloadProgress;
          onProgress(data);
        } catch {
          // Ignorer les lignes mal formées
        }
      }
    }
  }
}

export async function loadModel(modelId: string): Promise<{ model_id: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/llm/models/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model_id: modelId }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erreur inconnue" }));
    throw new Error(error.detail || "Erreur lors du chargement du modèle");
  }

  return response.json();
}
