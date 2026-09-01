import type { ComposeState, ConnectableProvider, MailProvider } from "../models";

const DEFAULT_COMPOSE_PROVIDER: ConnectableProvider = "gmail";

export function resolveComposeProvider(
  composeState: ComposeState,
  activeProvider: MailProvider,
): MailProvider {
  if (composeState.draft) return composeState.draft.provider as MailProvider;
  if (composeState.replyTo) return (composeState.replyTo.provider ?? DEFAULT_COMPOSE_PROVIDER) as MailProvider;
  return activeProvider === "all" ? DEFAULT_COMPOSE_PROVIDER : activeProvider;
}
