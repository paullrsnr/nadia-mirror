import { useState } from "react";
import { getHello } from "../services/apis/arch-health.api";

export default function Inbox() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    setError(null);

    try {
      const result = await getHello();
      setMessage(result);
    } catch (err) {
      setError("Erreur lors de l’appel API");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>📬 Nadia</h1>

      <button onClick={handleClick} disabled={loading}>
        {loading ? "Chargement..." : "Dire bonjour"}
      </button>

      {message && <p>Réponse backend : {message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
