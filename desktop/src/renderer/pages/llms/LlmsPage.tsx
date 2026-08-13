import "./LlmsPage.css";
import ModelCard from "../../components/domain/LlmModelCard";
import Button from "../../components/ui/Button";
import Loader from "../../components/ui/Loader";
import ErrorMessage from "../../components/ui/ErrorMessage";
import PageHeader from "../../components/ui/PageHeader";
import { useModelsData } from "./hooks/useModelsData";
import { useModelLoader } from "./hooks/useModelLoader";
import { useModelDownload } from "./hooks/useModelDownload";

export default function LlmsPage() {
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
    return (
      <div className="models-page-shell">
        <PageHeader title="Modèles IA" />
        <Loader fullPage label="Chargement des modèles..." />
      </div>
    );
  }

  const hasInstalledModels = installedModels.length > 0;

  /* ── Téléchargement initial en cours ── */
  if (!hasInstalledModels && initialDownload) {
    const progress = downloadProgress[initialDownload.id] || "Préparation...";
    const isKnownProgress = progress.includes("%");

    return (
      <div className="models-page-shell">
        <PageHeader title="Modèles IA" />
        <div className="models-download-screen scrollbar-hidden">
          <div
            className="models-download-spinner"
            style={{ width: 80, height: 80, borderWidth: 4 }}
          />
          <h2 className="models-download-title">
            Téléchargement de {initialDownload.name}
          </h2>
          <p className="models-download-desc">{initialDownload.description}</p>

          <div className="models-progress">
            <div
              className="models-progress__fill"
              style={{
                width: isKnownProgress ? progress : "100%",
                animation: isKnownProgress ? "none" : "pulse 1.5s ease-in-out infinite",
              }}
            />
          </div>
          <p className="models-progress__text">{progress}</p>
          <p className="models-download-footer">
            Le modèle sera chargé automatiquement une fois le téléchargement terminé
          </p>

          {error && <ErrorMessage message={error} className="models-download-footer" />}
        </div>
      </div>
    );
  }

  /* ── Aucun modèle installé — choix initial ── */
  if (!hasInstalledModels) {
    return (
      <div className="models-page-shell">
        <PageHeader title="Modèles IA" />
        <div className="models-no-models scrollbar-hidden">
          <div className="models-welcome">
            <div className="models-welcome__emoji">🤖</div>
            <h1 className="models-welcome__title">Bienvenue dans Nadia IA</h1>
            <p className="models-welcome__desc">
              Pour commencer, téléchargez un modèle d'intelligence artificielle
            </p>
          </div>

          {error && <ErrorMessage message={error} className="models-catalog-heading" />}

          <h2 className="models-catalog-heading">Choisissez un modèle pour démarrer</h2>

          {catalog.map((model) => (
            <Button
              type="button"
              key={model.id}
              variant="ghost"
              disabled={isDownloadingAny}
              onClick={() => handleDownload(model, true)}
              className="model-download-btn"
            >
              <div className="model-download-btn__row">
                <div>
                  <h3 className="model-download-btn__title">{model.name}</h3>
                  <p className="model-download-btn__desc">{model.description}</p>
                </div>
                <span className="model-download-btn__badge">Télécharger</span>
              </div>
            </Button>
          ))}
        </div>
      </div>
    );
  }

  /* ── Vue principale ── */
  return (
    <div className="models-page-shell">
      <PageHeader title="Modèles IA" />
      <div className="models-page scrollbar-hidden">
      {error && <ErrorMessage message={error} className="models-catalog-heading" />}

      <div className="models-active-section">
        <h2 className="models-active-section__title">Modèle actif</h2>
        <div className="models-active-section__row">
          <select
            value={status?.selected_model_id || ""}
            onChange={(e) => {
              const id = e.target.value;
              if (id && id !== status?.selected_model_id) handleLoad(id);
            }}
            disabled={loadingModel !== null}
            className="models-active-section__select"
            style={{ cursor: loadingModel ? "wait" : "pointer" }}
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
            <span className="models-active-section__status">
              <span className="models-active-section__status-icon">✓</span> Chargé
            </span>
          )}
        </div>

        {status?.selected_model_id && (
          <p className="models-active-section__desc">
            {findCatalogModel(status.selected_model_id)?.description || "Modèle personnalisé"}
          </p>
        )}
      </div>

      {availableCatalog.length > 0 && (
        <>
          <h2 className="models-catalog-title">Télécharger d'autres modèles</h2>
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

      {loadingModel && (
        <div className="models-overlay">
          <div className="models-overlay__modal">
            <div
              className="models-overlay__spinner"
              style={{ width: 40, height: 40, borderWidth: 3 }}
            />
            <p className="models-overlay__text">Chargement du modèle...</p>
            <p className="models-overlay__subtext">Cela peut prendre quelques secondes</p>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
