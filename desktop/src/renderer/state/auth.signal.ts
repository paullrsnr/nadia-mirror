import { signal, computed } from "@preact/signals-react";
import type { AuthStateByProvider } from "../types";

export const authSignal = signal<AuthStateByProvider>({
  gmail: null,
  outlook: null,
});

export const isAnyAuthenticated = computed(
  () =>
    authSignal.value.gmail?.is_authenticated === true ||
    authSignal.value.outlook?.is_authenticated === true,
);
