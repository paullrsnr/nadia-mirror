export const API_BASE_URL = "http://127.0.0.1:3333";

async function parseErrorMessage(response: Response): Promise<string> {
  const data = await response.json().catch(() => ({}));
  return (data as { detail?: string }).detail ?? `Erreur HTTP ${response.status}`;
}

export async function apiGet<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = params
    ? `${API_BASE_URL}${path}?${new URLSearchParams(params)}`
    : `${API_BASE_URL}${path}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }
  return response.json() as Promise<T>;
}

/** POST qui retourne un ReadableStream (téléchargement SSE). */
export async function apiPostStream(path: string, body: unknown): Promise<ReadableStreamDefaultReader<Uint8Array>> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }
  if (!response.body) {
    throw new Error("Stream non disponible");
  }
  return response.body.getReader();
}
