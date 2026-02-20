import { API_BASE_URL } from "./config";
import type { CatalogModel, LLMStatusResponse, DownloadProgress } from "../../models/llm";

export type {
  InstalledModel,
  CatalogModel,
  LLMStatusResponse,
  DownloadProgress,
} from "../../models/llm";

async function apiGet<T>(url: string, errorMessage: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(errorMessage);
  return response.json();
}

async function apiPost<T>(url: string, body: object, errorMessage: string): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail || errorMessage);
  }
  return response.json();
}

export async function getCatalog(): Promise<{ models: CatalogModel[] }> {
  return apiGet(`${API_BASE_URL}/llm/models/catalog`, "Erreur catalogue modèles");
}

type StreamEvent = { percent?: number; loaded?: number; total?: number; done?: boolean; path?: string; error?: string };

function parseSSEEvent(line: string): StreamEvent | null {
  if (!line.startsWith("data: ")) return null;
  try {
    return JSON.parse(line.slice(6)) as StreamEvent;
  } catch {
    return null;
  }
}

async function readSSEStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onEvent: (data: StreamEvent) => "done" | void
): Promise<void> {
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const block of parts) {
      for (const line of block.split("\n")) {
        const data = parseSSEEvent(line);
        if (data && onEvent(data) === "done") return;
      }
    }
  }
}

/**
 * Télécharge un modèle en stream et appelle onProgress au fur et à mesure.
 * Retourne une promesse résolue à la fin ou rejetée en cas d'erreur.
 */
export function downloadModelWithProgress(
  repo: string,
  filename: string,
  callbacks: { onProgress: (p: DownloadProgress) => void }
): Promise<{ path: string }> {
  return new Promise((resolve, reject) => {
    fetch(`${API_BASE_URL}/llm/models/download/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo, filename }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          reject(new Error((err as { detail?: string }).detail || "Erreur téléchargement"));
          return;
        }
        const reader = res.body?.getReader();
        if (!reader) {
          reject(new Error("Stream non disponible"));
          return;
        }
        await readSSEStream(reader, (data) => {
          if (data.error) {
            reject(new Error(data.error));
            return "done";
          }
          if (data.done && data.path) {
            resolve({ path: data.path });
            return "done";
          }
          if (typeof data.percent === "number" && data.loaded != null && data.total != null) {
            callbacks.onProgress({ percent: data.percent, loaded: data.loaded, total: data.total });
          }
        });
      })
      .catch(reject);
  });
}

export async function loadModel(modelId: string): Promise<{ model_id: string; message: string }> {
  return apiPost(`${API_BASE_URL}/llm/models/load`, { model_id: modelId }, "Erreur chargement modèle");
}

export async function getLLMStatus(): Promise<LLMStatusResponse> {
  return apiGet(`${API_BASE_URL}/llm/status`, "Erreur statut LLM");
}
