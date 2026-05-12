import { apiGet, apiPost, apiPostStream } from "./client";
import type { LlmStatus, CatalogModel, DownloadProgress, SummarizeResponse, ThreadMessage } from "../../models";

export async function getLlmStatus(): Promise<LlmStatus> {
  return apiGet("/llm/status");
}

export async function getCatalog(): Promise<CatalogModel[]> {
  return apiGet("/llm/models/catalog");
}

export async function summarizeEmail(
  subject: string,
  body: string,
  fromAddress = "",
): Promise<SummarizeResponse> {
  return apiPost("/llm/summarize", { subject, body, from_address: fromAddress });
}

export async function summarizeThread(
  subject: string,
  messages: ThreadMessage[],
): Promise<SummarizeResponse> {
  return apiPost("/llm/summarize-thread", { subject, messages });
}

export async function loadModel(modelId: string): Promise<{ model_id: string; message: string }> {
  return apiPost("/llm/models/load", { model_id: modelId });
}

export async function downloadModel(
  repo: string,
  filename: string,
  onProgress: (progress: DownloadProgress) => void,
): Promise<void> {
  const reader = await apiPostStream("/llm/models/download/stream", { repo, filename });
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6)) as DownloadProgress;
          onProgress(data);
        } catch {
          // Ligne mal formée — ignorée
        }
      }
    }
  }
}
