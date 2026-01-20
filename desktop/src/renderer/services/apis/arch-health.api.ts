const API_BASE_URL = "http://127.0.0.1:3333"; // A BOUGER PLUS TARD

export async function getHello(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/hello`);

  if (!response.ok) {
    throw new Error("API error");
  }

  const data = await response.json();
  return data.message;
}
