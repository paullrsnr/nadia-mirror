import type { CatalogModel, InstalledModel } from "../../types";

export interface ModelCardProps {
  model: CatalogModel;
  installed: InstalledModel | null;
  isSelected: boolean;
  isDownloading: boolean;
  downloadProgress: string | null;
  onDownload: () => void;
  onLoad: () => void;
}