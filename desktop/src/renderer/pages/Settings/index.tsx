import { useState, useEffect } from "react";
import AuthProviderCard from "../../components/domain/AuthProviderCard";
import Button from "../../components/ui/Button";
import ErrorMessage from "../../components/ui/ErrorMessage";
import { getAutoArchiveRules, saveAutoArchiveRules } from "../../services/api/autoArchive.api";
import { colors, spacing, radius } from "../../styles";
import { useAuth } from "./hooks/useAuth";

const PROVIDER_LABELS: Record<string, string> = {
  gmail: "Gmail",
  outlook: "Outlook",
};

export default function Settings() {
  const { authByProvider, loading, error, providers, connect, disconnect } = useAuth();
  const [archiveRules, setArchiveRules] = useState("");
  const [archiveRulesSaved, setArchiveRulesSaved] = useState(false);

  useEffect(() => {
    getAutoArchiveRules()
      .then((data) => setArchiveRules(data.rules))
      .catch(() => {});
  }, []);

  async function handleSaveArchiveRules() {
    await saveAutoArchiveRules(archiveRules);
    setArchiveRulesSaved(true);
    setTimeout(() => setArchiveRulesSaved(false), 2000);
  }

  return (
    <div style={{ padding: spacing.page }}>
      <h1>Paramètres</h1>

      {error && <ErrorMessage message={error} style={{ marginBottom: spacing.md }} />}

      {providers.map((provider) => (
        <AuthProviderCard
          key={provider}
          provider={provider}
          label={PROVIDER_LABELS[provider]}
          status={authByProvider[provider]}
          loading={loading[provider]}
          onConnect={() => connect(provider)}
          onDisconnect={() => disconnect(provider)}
        />
      ))}

      <div
        style={{
          marginTop: spacing.page,
          padding: spacing.page,
          border: `1px solid ${colors.borderStrong}`,
          borderRadius: radius.sm,
        }}
      >
        <h2 style={{ margin: `0 0 ${spacing.sm}px` }}>Archivage automatique (IA)</h2>
        <p style={{ margin: `0 0 ${spacing.sm}px`, color: colors.textSecondary, fontSize: "13px" }}>
          Décrivez les emails à archiver automatiquement. L'IA archivera directement les emails
          correspondants et vous demandera confirmation pour les cas incertains.
        </p>
        <p style={{ margin: `0 0 ${spacing.sm}px`, color: colors.textMuted, fontSize: "12px" }}>
          Exemples : "emails marketing et newsletters", "promotions Amazon et Spotify",
          "notifications automatiques sans action requise"
        </p>
        <textarea
          value={archiveRules}
          onChange={(e) => setArchiveRules(e.target.value)}
          placeholder="Ex : Archiver les newsletters, les emails promotionnels, et les notifications automatiques des réseaux sociaux."
          rows={4}
          style={{
            width: "100%",
            padding: spacing.sm,
            borderRadius: radius.sm,
            border: `1px solid ${colors.borderStrong}`,
            backgroundColor: colors.backgroundMuted,
            color: colors.textPrimary,
            fontSize: "13px",
            resize: "vertical",
            boxSizing: "border-box",
          }}
        />
        <Button onClick={handleSaveArchiveRules} style={{ marginTop: spacing.sm }}>
          {archiveRulesSaved ? "Enregistré ✓" : "Enregistrer les règles"}
        </Button>
      </div>
    </div>
  );
}
