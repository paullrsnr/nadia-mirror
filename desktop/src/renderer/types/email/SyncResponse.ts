export interface SyncResponse {
  status: "success" | "skipped" | "error";
  synced?: number;
  saved?: number;
  timestamp?: string;
  last_sync?: string;
  message?: string;
}
