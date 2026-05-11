import { useState, useCallback } from "react";
import { downloadModel } from "../../../services/api/llm.api";
import type { CatalogModel, DownloadProgress, UseModelDownloadResult, UseModelDownloadOptions } from "../../../models";

export function useModelDownload({
  refreshStatus,
  handleLoad,
}: UseModelDownloadOptions): UseModelDownloadResult {
  const [downloading, setDownloading] = useState<Partial<Record<string, boolean>>>({});
  const [downloadProgress, setDownloadProgress] = useState<Partial<Record<string, string>>>({});
  const [initialDownload, setInitialDownload] = useState<CatalogModel | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const isDownloadingAny = Object.values(downloading).some(Boolean);

  const handleDownload = useCallback(
    async (model: CatalogModel, isInitial = false): Promise<void> => {
      if (isInitial) setInitialDownload(model);
      setDownloading((prev) => ({ ...prev, [model.id]: true }));
      setDownloadProgress((prev) => ({ ...prev, [model.id]: "Connexion au serveur..." }));
      setDownloadError(null);

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
            setDownloadError(progress.error || "Erreur de téléchargement");
          }
        });

        const newStatus = await refreshStatus();
        if (isInitial && newStatus && newStatus.installed_models.length > 0) {
          await handleLoad(model.id);
        }
      } catch (err) {
        setDownloadError(err instanceof Error ? err.message : "Erreur de téléchargement");
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

  return {
    downloading,
    downloadProgress,
    initialDownload,
    isDownloadingAny,
    downloadError,
    handleDownload,
  };
}
