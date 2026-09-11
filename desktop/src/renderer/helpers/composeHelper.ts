import { CONNECTABLE_PROVIDERS } from "../constants/providers";
import type { ComposeState, ConnectableProvider, MailProvider } from "../models";

const DEFAULT_COMPOSE_PROVIDER: ConnectableProvider = "gmail";

function isConnectableProvider(value: string | undefined): value is ConnectableProvider {
  return CONNECTABLE_PROVIDERS.some((provider) => provider === value);
}

export function resolveComposeProvider(
  composeState: ComposeState,
  activeProvider: MailProvider,
): ConnectableProvider {
  if (composeState.draft) return composeState.draft.provider;
  if (composeState.replyTo) {
    return isConnectableProvider(composeState.replyTo.provider)
      ? composeState.replyTo.provider
      : DEFAULT_COMPOSE_PROVIDER;
  }
  return activeProvider === "all" ? DEFAULT_COMPOSE_PROVIDER : activeProvider;
}
