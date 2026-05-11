export interface DownloadProgress {
  status: "starting" | "progress" | "completed" | "exists" | "error";
  repo?: string;
  filename?: string;
  path?: string;
  progress?: number;
  error?: string;
}
