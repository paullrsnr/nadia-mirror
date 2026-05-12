import type { InstalledModel } from "./InstalledModel";

export interface LlmStatus {
  available: boolean;
  message: string;
  resolved_model_path: string | null;
  resolved_model_exists: boolean | null;
  resources_path: string | null;
  selected_model_id: string | null;
  installed_models: InstalledModel[];
}
