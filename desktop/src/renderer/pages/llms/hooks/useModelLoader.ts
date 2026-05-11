import { useState, useCallback } from "react";
import { loadModel } from "../../../services/api/llm.api";
import type { LlmStatus, UseModelLoaderResult } from "../../../models";

export function useModelLoader(
  refreshStatus: () => Promise<LlmStatus | null>,
): UseModelLoaderResult {
  const [loadingModel, setLoadingModel] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const handleLoad = useCallback(
    async (modelId: string): Promise<void> => {
      setLoadingModel(modelId);
      setLoadError(null);
      try {
        await loadModel(modelId);
        await refreshStatus();
      } catch (err) {
        setLoadError(err instanceof Error ? err.message : "Erreur de chargement");
      } finally {
        setLoadingModel(null);
      }
    },
    [refreshStatus],
  );

  return { loadingModel, loadError, handleLoad };
}
