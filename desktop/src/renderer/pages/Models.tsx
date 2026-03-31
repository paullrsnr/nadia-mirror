import { useState, useEffect, useCallback } from "react";
import { colors, spacing, radius, shadow } from "../theme";
import ModelCard from "../components/ModelCard";
import type { LlmStatus } from "../models/LlmStatus";
import type { CatalogModel } from "../models/CatalogModel";
import {
  getLlmStatus,
  getCatalog,
  downloadModel,
  loadModel,
  type DownloadProgress,
} from "../services/apis/llm.api";

const spinnerKeyframes = `
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
`;

export default function Models() {
  const [status, setStatus] = useState<LlmStatus | null>(null);
  const [catalog, setCatalog] = useState<CatalogModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<Record<string, boolean>>({});
  const [downloadProgress, setDownloadProgress] = useState<Record<string, string>>({});
  const [loadingModel, setLoadingModel] = useState<string | null>(null);
  const [initialDownload, setInitialDownload] = useState<CatalogModel | null>(null);

  const refreshStatus = useCallback(async () => {
    try {
      const newStatus = await getLlmStatus();
      setStatus(newStatus);
      return newStatus;
    } catch (err) {
      console.error("Erreur statut LLM:", err);
      return null;
    }
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statusData, catalogData] = await Promise.all([getLlmStatus(), getCatalog()]);
      setStatus(statusData);
      setCatalog(catalogData);
    } catch (err) {
      setError("Impossible de charger les données LLM");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const findCatalogModel = (modelId: string): CatalogModel | undefined => {
    return catalog.find((m) => {
      const filenameWithoutExt = m.filename.replace(/\.gguf$/i, "");
      return m.id === modelId || filenameWithoutExt === modelId;
    });
  };

  const isModelInstalled = (model: CatalogModel): boolean => {
    if (!status) return false;
    const filenameWithoutExt = model.filename.replace(/\.gguf$/i, "");
    return status.installed_models.some(
      (m) => m.id === model.id || m.id === filenameWithoutExt || m.name === model.filename
    );
  };

  const handleDownload = async (model: CatalogModel, isInitial: boolean = false) => {
    if (isInitial) {
      setInitialDownload(model);
    }
    setDownloading((prev) => ({ ...prev, [model.id]: true }));
    setDownloadProgress((prev) => ({ ...prev, [model.id]: "Connexion au serveur..." }));
    setError(null);

    try {
      await downloadModel(model.repo, model.filename, (progress: DownloadProgress) => {
        if (progress.status === "starting") {
          setDownloadProgress((prev) => ({ ...prev, [model.id]: "Téléchargement en cours..." }));
        } else if (progress.status === "progress" && progress.progress !== undefined) {
          const pct = progress.progress;
          setDownloadProgress((prev) => ({
            ...prev,
            [model.id]: `${Math.round(pct)}%`,
          }));
        } else if (progress.status === "completed" || progress.status === "exists") {
          setDownloadProgress((prev) => ({ ...prev, [model.id]: "Terminé !" }));
        } else if (progress.status === "error") {
          setError(progress.error || "Erreur de téléchargement");
        }
      });

      const newStatus = await refreshStatus();
      
      if (isInitial && newStatus && newStatus.installed_models.length > 0) {
        await handleLoad(model.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur de téléchargement");
    } finally {
      setDownloading((prev) => ({ ...prev, [model.id]: false }));
      setDownloadProgress((prev) => {
        const copy = { ...prev };
        delete copy[model.id];
        return copy;
      });
      setInitialDownload(null);
    }
  };

  const handleLoad = async (modelId: string) => {
    setLoadingModel(modelId);
    setError(null);

    try {
      await loadModel(modelId);
      await refreshStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur de chargement");
    } finally {
      setLoadingModel(null);
    }
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const modelId = e.target.value;
    if (modelId && modelId !== status?.selected_model_id) {
      handleLoad(modelId);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: spacing.page, textAlign: "center" }}>
        <p style={{ color: colors.textMuted }}>Chargement...</p>
      </div>
    );
  }

  const installedModels = status?.installed_models || [];
  const hasInstalledModels = installedModels.length > 0;
  const availableCatalog = catalog.filter((model) => !isModelInstalled(model));
  const isDownloadingAny = Object.values(downloading).some(Boolean);

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
        <style>{spinnerKeyframes}</style>
        
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
        
        <h2 style={{ margin: 0, marginBottom: spacing.sm, color: colors.textPrimary }}>
          Téléchargement de {initialDownload.name}
        </h2>
        
        <p
          style={{
            margin: 0,
            marginBottom: spacing.page,
            color: colors.textSecondary,
            fontSize: "14px",
            maxWidth: 400,
          }}
        >
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
        
        <p
          style={{
            margin: 0,
            color: colors.textMuted,
            fontSize: "16px",
            fontWeight: "bold",
          }}
        >
          {progress}
        </p>
        
        <p
          style={{
            margin: 0,
            marginTop: spacing.lg,
            color: colors.textMuted,
            fontSize: "12px",
          }}
        >
          Le modèle sera chargé automatiquement une fois le téléchargement terminé
        </p>

        {error && (
          <div
            style={{
              marginTop: spacing.page,
              padding: spacing.card,
              backgroundColor: "#ffebee",
              color: colors.error,
              borderRadius: 8,
              maxWidth: 400,
            }}
          >
            {error}
          </div>
        )}
      </div>
    );
  }

  if (!hasInstalledModels) {
    return (
      <div style={{ padding: spacing.page }}>
        <style>{spinnerKeyframes}</style>
        
        <div
          style={{
            textAlign: "center",
            padding: spacing.lg,
            marginBottom: spacing.page,
          }}
        >
          <div style={{ fontSize: 48, marginBottom: spacing.md }}>🤖</div>
          <h1 style={{ margin: 0, marginBottom: spacing.sm }}>Bienvenue dans Nadia IA</h1>
          <p style={{ margin: 0, color: colors.textSecondary, fontSize: "15px" }}>
            Pour commencer, téléchargez un modèle d'intelligence artificielle
          </p>
        </div>

        {error && (
          <div
            style={{
              marginBottom: spacing.card,
              padding: spacing.card,
              backgroundColor: "#ffebee",
              color: colors.error,
              borderRadius: 8,
            }}
          >
            {error}
          </div>
        )}

        <h2 style={{ fontSize: "16px", marginBottom: spacing.card, color: colors.textSecondary }}>
          Choisissez un modèle pour démarrer
        </h2>

        {catalog.map((model) => (
          <button
            key={model.id}
            type="button"
            disabled={isDownloadingAny}
            onClick={() => handleDownload(model, true)}
            style={{
              display: "block",
              width: "100%",
              padding: spacing.card,
              marginBottom: spacing.md,
              border: `1px solid ${colors.border}`,
              borderRadius: radius.md,
              backgroundColor: colors.background,
              boxShadow: shadow.card,
              cursor: isDownloadingAny ? "default" : "pointer",
              transition: "border-color 0.2s, box-shadow 0.2s",
              textAlign: "left",
            }}
            onMouseEnter={(e) => {
              if (!isDownloadingAny) {
                e.currentTarget.style.borderColor = colors.buttonPrimary;
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,123,255,0.15)";
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = colors.border;
              e.currentTarget.style.boxShadow = shadow.card;
            }}
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
                  padding: `${spacing.sm}px ${spacing.card}px`,
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

  return (
    <div style={{ padding: spacing.page }}>
      <h1 style={{ marginBottom: spacing.sm }}>Modèles LLM</h1>

      {error && (
        <div
          style={{
            marginBottom: spacing.card,
            padding: spacing.card,
            backgroundColor: "#ffebee",
            color: colors.error,
            borderRadius: 8,
          }}
        >
          {error}
        </div>
      )}

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
        <h2 style={{ fontSize: "16px", margin: 0, marginBottom: spacing.md, color: colors.textPrimary }}>
          Modèle actif
        </h2>

        <div style={{ display: "flex", alignItems: "center", gap: spacing.md }}>
          <select
            value={status?.selected_model_id || ""}
            onChange={handleSelectChange}
            disabled={loadingModel !== null}
            style={{
              flex: 1,
              maxWidth: 400,
              padding: `${spacing.sm}px ${spacing.md}px`,
              fontSize: "14px",
              border: `1px solid ${colors.borderStrong}`,
              borderRadius: radius.sm,
              backgroundColor: colors.background,
              cursor: loadingModel ? "wait" : "pointer",
            }}
          >
            <option value="">-- Sélectionner un modèle --</option>
            {installedModels.map((model) => {
              const catalogInfo = findCatalogModel(model.id);
              return (
                <option key={model.id} value={model.id}>
                  {catalogInfo?.name || model.name}
                </option>
              );
            })}
          </select>

          {status?.selected_model_id && (
            <span
              style={{
                display: "flex",
                alignItems: "center",
                gap: spacing.xs,
                color: colors.success,
                fontSize: "13px",
              }}
            >
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

      {loadingModel && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
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
              borderRadius: 8,
              textAlign: "center",
            }}
          >
            <style>{spinnerKeyframes}</style>
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
