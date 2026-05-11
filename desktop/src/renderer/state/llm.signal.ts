import { signal, computed } from "@preact/signals-react";
import type { LlmStatus } from "../models";

export const llmStatusSignal = signal<LlmStatus | null>(null);

export const selectedModelId = computed(
  () => llmStatusSignal.value?.selected_model_id ?? null,
);

export const isLlmAvailable = computed(
  () => llmStatusSignal.value?.available === true,
);
