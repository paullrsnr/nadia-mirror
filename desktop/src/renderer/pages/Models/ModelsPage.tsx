import ModelCard from "../../components/domain/LlmModelCard";
import Loader from "../../components/ui/Loader";
import ErrorMessage from "../../components/ui/ErrorMessage";
import { colors, spacing, radius, shadow } from "../../styles";
import { useModelsData } from "./hooks/useModelsData";
import { useModelLoader } from "./hooks/useModelLoader";
import { useModelDownload } from "./hooks/useModelDownload";

export default function ModelsPage() {
  const {
    status,
    catalog,
    loading,
    error: dataError,
    installedModels,
    availableCatalog,
    findCatalogModel,
    refreshStatus,
  } = useModelsData();

  const { loadingModel, loadError, handleLoad } = useModelLoader(refreshStatus);

  const {
    downloading,
    downloadProgress,
    initialDownload,
    isDownloadingAny,
    downloadError,
    handleDownload,
  } = useModelDownload({ refreshStatus, handleLoad });

  const error = dataError ?? loadError ?? downloadError;

  if (loading) {
    return <Loader fullPage label="Chargement des modèles..." />;
  }

  const hasInstalledModels = installedModels.length > 0;

  /* ── Téléchargement initial en cours ── */
  if (!hasInstalledModels && initialDownload) {
    const progress = downloadProgress[initialDownload.id] || "Préparation...";

    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "80vh",
          padding: spacing.page,
          textAlign: "center",
        }}
      >
        <div
          style={{
            width: 80,
            height: 80,
            border: `4px solid ${colors.border}`,
            borderTop: `4px solid ${colors.buttonPrimary}`,
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
            marginBottom: spacing.lg,
          }}
        />
        <h2 style={{ margin: 0, marginBottom: spacing.sm }}>
          Téléchargement de {initialDownload.name}
        </h2>
        <p style={{ margin: 0, marginBottom: spacing.page, color: colors.textSecondary, fontSize: "14px", maxWidth: 400 }}>
          {initialDownload.description}
        </p>
        <div
          style={{
            width: "100%",
            maxWidth: 400,
            height: 8,
            backgroundColor: colors.border,
            borderRadius: 4,
            overflow: "hidden",
            marginBottom: spacing.md,
          }}
        >
          <div
            style={{
              height: "100%",
              backgroundColor: colors.buttonPrimary,
              width: progress.includes("%") ? progress : "100%",
              animation: progress.includes("%") ? "none" : "pulse 1.5s ease-in-out infinite",
              transition: "width 0.3s ease",
            }}
          />
        </div>
        <p style={{ margin: 0, color: colors.textMuted, fontSize: "16px", fontWeight: "bold" }}>
          {progress}
        </p>
        <p style={{ margin: 0, marginTop: spacing.lg, color: colors.textMuted, fontSize: "12px" }}>
          Le modèle sera chargé automatiquement une fois le téléchargement terminé
        </p>
        {error && (
          <ErrorMessage message={error} style={{ marginTop: spacing.page, maxWidth: 400 }} />
        )}
      </div>
    );
  }

  /* ── Aucun modèle installé — choix initial ── */
  if (!hasInstalledModels) {
    return (
      <div style={{ padding: spacing.page }}>
        <div style={{ textAlign: "center", padding: spacing.lg, marginBottom: spacing.page }}>
          <div style={{ fontSize: 48, marginBottom: spacing.md }}>🤖</div>
          <h1 style={{ margin: 0, marginBottom: spacing.sm }}>Bienvenue dans Nadia IA</h1>
          <p style={{ margin: 0, color: colors.textSecondary, fontSize: "15px" }}>
            Pour commencer, téléchargez un modèle d'intelligence artificielle
          </p>
        </div>

        {error && <ErrorMessage message={error} style={{ marginBottom: spacing.card }} />}

        <h2 style={{ fontSize: "16px", marginBottom: spacing.card, color: colors.textSecondary }}>
          Choisissez un modèle pour démarrer
        </h2>

        {catalog.map((model) => (
          <button
            key={model.id}
            type="button"
            disabled={isDownloadingAny}
            onClick={() => handleDownload(model, true)}
            className="model-download-btn"
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 style={{ margin: 0, marginBottom: spacing.xs, color: colors.textPrimary }}>
                  {model.name}
                </h3>
                <p style={{ margin: 0, color: colors.textSecondary, fontSize: "13px" }}>
                  {model.description}
                </p>
              </div>
              <span
                style={{
                  padding: `${spacing.sm} ${spacing.card}`,
                  backgroundColor: colors.buttonPrimary,
                  color: "white",
                  borderRadius: radius.sm,
                  fontSize: "13px",
                }}
              >
                Télécharger
              </span>
            </div>
          </button>
        ))}
      </div>
    );
  }

  /* ── Vue principale ── */
  return (
    <div style={{ padding: spacing.page }}>
      <h1 style={{ marginBottom: spacing.sm }}>Modèles LLM</h1>

      {error && <ErrorMessage message={error} style={{ marginBottom: spacing.card }} />}

      {/* Modèle actif */}
      <div
        style={{
          marginBottom: spacing.page,
          padding: spacing.card,
          backgroundColor: colors.background,
          border: `1px solid ${colors.border}`,
          borderRadius: radius.md,
          boxShadow: shadow.card,
        }}
      >
        <h2 style={{ fontSize: "16px", margin: 0, marginBottom: spacing.md }}>Modèle actif</h2>
        <div style={{ display: "flex", alignItems: "center", gap: spacing.md }}>
          <select
            value={status?.selected_model_id || ""}
            onChange={(e) => {
              const id = e.target.value;
              if (id && id !== status?.selected_model_id) handleLoad(id);
            }}
            disabled={loadingModel !== null}
            style={{
              flex: 1,
              maxWidth: 400,
              padding: `${spacing.sm} ${spacing.md}`,
              fontSize: "14px",
              border: `1px solid ${colors.borderStrong}`,
              borderRadius: radius.sm,
              backgroundColor: colors.background,
              cursor: loadingModel ? "wait" : "pointer",
            }}
          >
            <option value="">-- Sélectionner un modèle --</option>
            {installedModels.map((model) => {
              const info = findCatalogModel(model.id);
              return (
                <option key={model.id} value={model.id}>
                  {info?.name || model.name}
                </option>
              );
            })}
          </select>

          {status?.selected_model_id && (
            <span style={{ display: "flex", alignItems: "center", gap: spacing.xs, color: colors.success, fontSize: "13px" }}>
              <span style={{ fontSize: "16px" }}>✓</span> Chargé
            </span>
          )}
        </div>

        {status?.selected_model_id && (
          <p style={{ margin: 0, marginTop: spacing.sm, color: colors.textMuted, fontSize: "12px" }}>
            {findCatalogModel(status.selected_model_id)?.description || "Modèle personnalisé"}
          </p>
        )}
      </div>

      {/* Catalogue */}
      {availableCatalog.length > 0 && (
        <>
          <h2 style={{ fontSize: "18px", marginBottom: spacing.card, color: colors.textSecondary }}>
            Télécharger d'autres modèles
          </h2>
          {availableCatalog.map((model) => (
            <ModelCard
              key={model.id}
              model={model}
              installed={null}
              isSelected={false}
              isDownloading={downloading[model.id] || false}
              downloadProgress={downloadProgress[model.id] || null}
              onDownload={() => handleDownload(model)}
              onLoad={() => {}}
            />
          ))}
        </>
      )}

      {/* Overlay chargement modèle */}
      {loadingModel && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div
            style={{
              backgroundColor: colors.background,
              padding: spacing.lg,
              borderRadius: radius.md,
              textAlign: "center",
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                border: `3px solid ${colors.border}`,
                borderTop: `3px solid ${colors.buttonPrimary}`,
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
                margin: "0 auto",
                marginBottom: spacing.md,
              }}
            />
            <p style={{ margin: 0, fontSize: "16px" }}>Chargement du modèle...</p>
            <p style={{ margin: 0, marginTop: spacing.sm, color: colors.textMuted, fontSize: "13px" }}>
              Cela peut prendre quelques secondes
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
