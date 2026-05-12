import { useState, useEffect, useCallback } from "react";
import { useComputed } from "@preact/signals-react";
import { getLlmStatus, getCatalog } from "../../../services/api/llm.api";
import { llmStatusSignal } from "../../../state";
import type { LlmStatus, CatalogModel, InstalledModel, UseModelsDataResult } from "../../../models";

export function useModelsData(): UseModelsDataResult {
  const statusComputed = useComputed(() => llmStatusSignal.value);
  const status = statusComputed.value;
  const [catalog, setCatalog] = useState<CatalogModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshStatus = useCallback(async (): Promise<LlmStatus | null> => {
    try {
      const newStatus = await getLlmStatus();
      llmStatusSignal.value = newStatus;
      return newStatus;
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([getLlmStatus(), getCatalog()])
      .then(([statusData, catalogData]) => {
        llmStatusSignal.value = statusData;
        setCatalog(catalogData);
      })
      .catch(() => setError("Impossible de charger les données LLM"))
      .finally(() => setLoading(false));
  }, []);

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
        (m: InstalledModel) => m.id === model.id || m.id === base || m.name === model.filename,
      );
    },
    [status],
  );

  const installedModels: InstalledModel[] = status?.installed_models ?? [];
  const availableCatalog = catalog.filter((m) => !isModelInstalled(m));

  return {
    status,
    catalog,
    loading,
    error,
    installedModels,
    availableCatalog,
    findCatalogModel,
    isModelInstalled,
    refreshStatus,
  };
}
