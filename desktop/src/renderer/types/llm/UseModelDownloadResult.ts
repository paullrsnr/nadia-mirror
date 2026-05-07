import type { CatalogModel } from ".";

export interface UseModelDownloadResult {
  downloading: Record<string, boolean>;
  downloadProgress: Record<string, string>;
  initialDownload: CatalogModel | null;
  isDownloadingAny: boolean;
  downloadError: string | null;
  handleDownload: (model: CatalogModel, isInitial?: boolean) => Promise<void>;
}
