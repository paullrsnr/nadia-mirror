import { API_BASE_URL } from "./config";

export async function checkHealth(): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.ok;
}

// getHello - À implémenter
