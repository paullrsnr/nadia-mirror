import "./AuthProviderCard.css";
import Button from "../ui/Button";
import type { AuthProviderCardProps } from "../../models/auth/AuthProviderCardProps";

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
    <section aria-labelledby={`auth-${provider}-title`} className="auth-card">
      <h2 id={`auth-${provider}-title`} className="auth-card__title">
        Connexion {label}
      </h2>

      <div className="auth-card__body">
        {isConnected ? (
          <>
            <p className="auth-card__status--connected">
              Connecté {status?.email ? `— ${status.email}` : ""}
            </p>
            <Button variant="secondary" onClick={onDisconnect} disabled={loading} className="self-start">
              {loading ? "Déconnexion..." : "Déconnecter"}
            </Button>
          </>
        ) : (
          <>
            <p className="auth-card__status--disconnected">Non connecté</p>
            <Button variant="primary" onClick={onConnect} disabled={loading} className="self-start">
              {loading ? "Connexion..." : `Se connecter à ${label}`}
            </Button>
          </>
        )}

        {children != null && (
          <div className="auth-card__children">{children}</div>
        )}
      </div>
    </section>
  );
}
