import type { LlmStatus, CatalogModel, InstalledModel } from ".";

export interface UseModelsDataResult {
  status: LlmStatus | null;
  catalog: CatalogModel[];
  loading: boolean;
  error: string | null;
  installedModels: InstalledModel[];
  availableCatalog: CatalogModel[];
  findCatalogModel: (modelId: string) => CatalogModel | undefined;
  isModelInstalled: (model: CatalogModel) => boolean;
  refreshStatus: () => Promise<LlmStatus | null>;
}
