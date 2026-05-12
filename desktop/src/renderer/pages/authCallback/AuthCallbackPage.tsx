import "./AuthCallbackPage.css";
import { useEffect } from "react";

export default function AuthCallbackPage() {
  const params = new URLSearchParams(window.location.search);
  const success = params.get("success") === "1";
  const errorMsg = params.get("error");

  useEffect(() => {
    const t = setTimeout(() => window.close(), 2000);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="auth-callback">
      <div className="auth-callback__card">
        {success ? (
          <>
            <h1 className="auth-callback__title--success">✓ Authentification réussie !</h1>
            <p>Vous pouvez fermer cette fenêtre et retourner à l'application.</p>
          </>
        ) : (
          <>
            <h1 className="auth-callback__title--error">✗ Erreur d'authentification</h1>
            <p>{errorMsg || "Une erreur est survenue."}</p>
            <p>Veuillez réessayer.</p>
          </>
        )}
      </div>
    </div>
  );
}
