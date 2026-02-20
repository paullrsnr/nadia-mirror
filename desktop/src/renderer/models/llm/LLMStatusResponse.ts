import type { InstalledModel } from "./InstalledModel";

/** Réponse de l'endpoint statut LLM. */
export interface LLMStatusResponse {
  available: boolean;
  message: string;
  selected_model_id?: string | null;
  installed_models?: InstalledModel[];
}
