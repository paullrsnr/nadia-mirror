import React, { useEffect } from "react";
import { colors, spacing, typography, radius, shadow } from "../theme";

/**
 * Page affichée après redirection du backend OAuth (succès ou erreur).
 * Affiche le message et ferme la fenêtre (popup) après 2 secondes.
 */
export default function AuthCallback() {
  const params = new URLSearchParams(window.location.search);
  const success = params.get("success") === "1";
  const errorMsg = params.get("error");

  useEffect(() => {
    const t = setTimeout(() => {
      window.close();
    }, 2000);
    return () => clearTimeout(t);
  }, []);

  return (
    <div
      style={{
        fontFamily: typography.fontFamily,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        margin: 0,
        background: colors.backgroundOverlay,
      }}
    >
      <div
        style={{
          textAlign: "center",
          padding: spacing.lg,
          background: colors.background,
          borderRadius: radius.md,
          boxShadow: shadow.card,
        }}
      >
        {success ? (
          <>
            <h1 style={{ color: colors.success }}>✓ Authentification réussie !</h1>
            <p>Vous pouvez fermer cette fenêtre et retourner à l'application.</p>
          </>
        ) : (
          <>
            <h1 style={{ color: colors.error }}>✗ Erreur d'authentification</h1>
            <p>{errorMsg || "Une erreur est survenue."}</p>
            <p>Veuillez réessayer.</p>
          </>
        )}
      </div>
    </div>
  );
}
