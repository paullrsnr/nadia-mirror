import "./LlmModelCard.css";
import type { ModelCardProps } from "../../models/llm";
import Button from "../ui/Button";

export default function LlmModelCard({
  model,
  installed,
  isSelected,
  isDownloading,
  downloadProgress,
  onDownload,
  onLoad,
}: ModelCardProps) {
  const isInstalled = installed !== null;

  return (
    <div className={`model-card${isSelected ? " model-card--selected" : ""}`}>
      <div className="model-card__header">
        <div className="model-card__info">
          <h3 className="model-card__title">
            {model.name}
            {isSelected && (
              <span className="model-card__active-badge">● Actif</span>
            )}
          </h3>
          <p className="model-card__desc">{model.description}</p>
          <p className="model-card__meta">{model.repo} / {model.filename}</p>
        </div>

        <div className="model-card__actions">
          {!isInstalled && !isDownloading && (
            <Button variant="primary" size="sm" onClick={onDownload}>
              Télécharger
            </Button>
          )}

          {isDownloading && (
            <span className="model-card__progress">
              {downloadProgress || "Téléchargement..."}
            </span>
          )}

          {isInstalled && !isSelected && (
            <Button variant="success" size="sm" onClick={onLoad}>
              Charger
            </Button>
          )}

          {isInstalled && (
            <span className="model-card__installed-badge">Installé</span>
          )}
        </div>
      </div>
    </div>
  );
}
