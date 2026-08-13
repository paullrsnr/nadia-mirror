import type { ConnectableProvider } from "../models/auth";

export const CONNECTABLE_PROVIDERS: ConnectableProvider[] = ["gmail", "outlook"];

export const PROVIDER_LABELS: Record<ConnectableProvider, string> = {
  gmail: "Gmail",
  outlook: "Outlook",
};
