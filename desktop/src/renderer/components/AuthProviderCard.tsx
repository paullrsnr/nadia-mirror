import React from "react";
import { colors, spacing, radius } from "../theme";
import type { AuthStatus } from "../models";
import type { ConnectableProvider } from "../services/auth";

export interface AuthProviderCardProps {
  readonly provider: ConnectableProvider;
  readonly label: string;
  readonly status: AuthStatus | null;
  readonly loading: boolean;
  readonly onConnect: () => void;
  readonly onDisconnect: () => void;
  /** Zone optionnelle pour contenu futur (avatar, autre source d'auth, etc.) */
  readonly children?: React.ReactNode;
}

const CARD_MIN_HEIGHT = 140;

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
        minHeight: CARD_MIN_HEIGHT,
        padding: spacing.page,
        marginTop: spacing.lg,
        backgroundColor: colors.backgroundMuted,
        border: `1px solid ${colors.borderStrong}`,
        borderRadius: radius.md,
        boxSizing: "border-box",
      }}
    >
      <h2 id={`auth-${provider}-title`} style={{ margin: 0, marginBottom: spacing.md, fontSize: "1.1rem" }}>
        Connexion {label}
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: spacing.md }}>
        {isConnected ? (
          <>
            <p style={{ margin: 0, color: colors.success }}>
              Connecté {status?.email ? `— ${status.email}` : ""}
            </p>
            <button
              type="button"
              onClick={onDisconnect}
              disabled={loading}
              style={{
                alignSelf: "flex-start",
                padding: `${spacing.sm}px ${spacing.card}px`,
                backgroundColor: colors.buttonSecondary,
                color: colors.textPrimary,
                border: `1px solid ${colors.borderButton}`,
                borderRadius: radius.sm,
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? "Déconnexion..." : "Déconnecter"}
            </button>
          </>
        ) : (
          <>
            <p style={{ margin: 0, color: colors.textMuted }}>Non connecté</p>
            <button
              type="button"
              onClick={onConnect}
              disabled={loading}
              style={{
                alignSelf: "flex-start",
                padding: `${spacing.sm}px ${spacing.card}px`,
                backgroundColor: colors.buttonPrimary,
                color: colors.background,
                border: "none",
                borderRadius: radius.sm,
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? "Connexion..." : `Se connecter à ${label}`}
            </button>
          </>
        )}

        {children != null && (
          <div style={{ marginTop: spacing.sm, paddingTop: spacing.md, borderTop: `1px solid ${colors.border}` }}>
            {children}
          </div>
        )}
      </div>
    </section>
  );
}
