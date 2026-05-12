import type { CatalogModel } from "./CatalogModel";
import type { InstalledModel } from "./InstalledModel";

export interface ModelCardProps {
  model: CatalogModel;
  installed: InstalledModel | null;
  isSelected: boolean;
  isDownloading: boolean;
  downloadProgress: string | null;
  onDownload: () => void;
  onLoad: () => void;
}