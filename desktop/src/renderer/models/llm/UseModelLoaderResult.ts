export interface UseModelLoaderResult {
  loadingModel: string | null;
  loadError: string | null;
  handleLoad: (modelId: string) => Promise<void>;
}
