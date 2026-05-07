import { colors, spacing, radius } from "../../styles";
import Button from "../ui/Button";
import type { AuthProviderCardProps } from "../../types/auth/AuthProviderCardProps";

export default function AuthProviderCard({
  provider,
  label,
  status,
  loading,
  onConnect,
  onDisconnect,
  children,
}: AuthProviderCardProps) {
  const isConnected = status?.is_authenticated ?? false;

  return (
    <section
      aria-labelledby={`auth-${provider}-title`}
      style={{
        padding: spacing.page,
        marginTop: spacing.lg,
        backgroundColor: colors.backgroundMuted,
        border: `1px solid ${colors.borderStrong}`,
        borderRadius: radius.md,
      }}
    >
      <h2
        id={`auth-${provider}-title`}
        style={{ margin: 0, marginBottom: spacing.md, fontSize: "1.1rem" }}
      >
        Connexion {label}
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: spacing.md }}>
        {isConnected ? (
          <>
            <p style={{ margin: 0, color: colors.success }}>
              Connecté {status?.email ? `— ${status.email}` : ""}
            </p>
            <Button
              variant="secondary"
              onClick={onDisconnect}
              disabled={loading}
              style={{ alignSelf: "flex-start" }}
            >
              {loading ? "Déconnexion..." : "Déconnecter"}
            </Button>
          </>
        ) : (
          <>
            <p style={{ margin: 0, color: colors.textMuted }}>Non connecté</p>
            <Button
              variant="primary"
              onClick={onConnect}
              disabled={loading}
              style={{ alignSelf: "flex-start" }}
            >
              {loading ? "Connexion..." : `Se connecter à ${label}`}
            </Button>
          </>
        )}

        {children != null && (
          <div
            style={{
              marginTop: spacing.sm,
              paddingTop: spacing.md,
              borderTop: `1px solid ${colors.border}`,
            }}
          >
            {children}
          </div>
        )}
      </div>
    </section>
  );
}
