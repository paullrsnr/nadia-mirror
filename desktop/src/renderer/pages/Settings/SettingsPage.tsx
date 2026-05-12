import "./SettingsPage.css";
import { useState, useEffect } from "react";
import AuthProviderCard from "../../components/domain/AuthProviderCard";
import Button from "../../components/ui/Button";
import ErrorMessage from "../../components/ui/ErrorMessage";
import { getAutoArchiveRules, saveAutoArchiveRules } from "../../services/api/autoArchive.api";
import { useAuth } from "./hooks/useAuth";
import type { ConnectableProvider } from "../../models/auth";

const PROVIDER_LABELS: Record<ConnectableProvider, string> = {
  gmail: "Gmail",
  outlook: "Outlook",
};

export default function SettingsPage() {
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
    <div className="settings-page">
      <h1>Paramètres</h1>

      {error && <ErrorMessage message={error} className="settings-section__save" />}

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

      <div className="settings-section">
        <h2 className="settings-section__title">Archivage automatique (IA)</h2>
        <p className="settings-section__desc">
          Décrivez les emails à archiver automatiquement. L'IA archivera directement les emails
          correspondants et vous demandera confirmation pour les cas incertains.
        </p>
        <p className="settings-section__examples">
          Exemples : "emails marketing et newsletters", "promotions Amazon et Spotify",
          "notifications automatiques sans action requise"
        </p>
        <textarea
          value={archiveRules}
          onChange={(e) => setArchiveRules(e.target.value)}
          placeholder="Ex : Archiver les newsletters, les emails promotionnels, et les notifications automatiques des réseaux sociaux."
          rows={4}
          className="settings-section__textarea"
        />
        <Button onClick={handleSaveArchiveRules} className="settings-section__save">
          {archiveRulesSaved ? "Enregistré ✓" : "Enregistrer les règles"}
        </Button>
      </div>
    </div>
  );
}
