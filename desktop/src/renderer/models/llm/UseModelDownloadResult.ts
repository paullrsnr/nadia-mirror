import type { CatalogModel } from ".";

export interface UseModelDownloadResult {
  downloading: Partial<Record<string, boolean>>;
  downloadProgress: Partial<Record<string, string>>;
  initialDownload: CatalogModel | null;
  isDownloadingAny: boolean;
  downloadError: string | null;
  handleDownload: (model: CatalogModel, isInitial?: boolean) => Promise<void>;
}
