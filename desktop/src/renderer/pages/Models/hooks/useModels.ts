import { useState, useEffect, useCallback } from "react";
import { getLlmStatus, getCatalog, downloadModel, loadModel } from "../../../services/api/llm.api";
import type { LlmStatus, CatalogModel, DownloadProgress } from "../../../types";

export function useModels() {
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
    } catch {
      return null;
    }
  }, []);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statusData, catalogData] = await Promise.all([getLlmStatus(), getCatalog()]);
      setStatus(statusData);
      setCatalog(catalogData);
    } catch {
      setError("Impossible de charger les données LLM");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const findCatalogModel = useCallback(
    (modelId: string): CatalogModel | undefined =>
      catalog.find((m) => {
        const base = m.filename.replace(/\.gguf$/i, "");
        return m.id === modelId || base === modelId;
      }),
    [catalog],
  );

  const isModelInstalled = useCallback(
    (model: CatalogModel): boolean => {
      if (!status) return false;
      const base = model.filename.replace(/\.gguf$/i, "");
      return status.installed_models.some(
        (m) => m.id === model.id || m.id === base || m.name === model.filename,
      );
    },
    [status],
  );

  const handleLoad = useCallback(
    async (modelId: string) => {
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
    },
    [refreshStatus],
  );

  const handleDownload = useCallback(
    async (model: CatalogModel, isInitial = false) => {
      if (isInitial) setInitialDownload(model);
      setDownloading((prev) => ({ ...prev, [model.id]: true }));
      setDownloadProgress((prev) => ({ ...prev, [model.id]: "Connexion au serveur..." }));
      setError(null);

      try {
        await downloadModel(model.repo, model.filename, (progress: DownloadProgress) => {
          if (progress.status === "starting") {
            setDownloadProgress((prev) => ({ ...prev, [model.id]: "Téléchargement en cours..." }));
          } else if (progress.status === "progress" && progress.progress !== undefined) {
            setDownloadProgress((prev) => ({
              ...prev,
              [model.id]: `${Math.round(progress.progress!)}%`,
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
    },
    [refreshStatus, handleLoad],
  );

  const installedModels = status?.installed_models ?? [];
  const availableCatalog = catalog.filter((m) => !isModelInstalled(m));
  const isDownloadingAny = Object.values(downloading).some(Boolean);

  return {
    status,
    catalog,
    loading,
    error,
    downloading,
    downloadProgress,
    loadingModel,
    initialDownload,
    installedModels,
    availableCatalog,
    isDownloadingAny,
    findCatalogModel,
    isModelInstalled,
    handleDownload,
    handleLoad,
  };
}
