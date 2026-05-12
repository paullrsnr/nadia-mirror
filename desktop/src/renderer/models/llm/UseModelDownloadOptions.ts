import type { LlmStatus } from "./LlmStatus";

export interface UseModelDownloadOptions {
  refreshStatus: () => Promise<LlmStatus | null>;
  handleLoad: (modelId: string) => Promise<void>;
}
