export type {
  EmailAddress,
  EmailAttachment,
  Email,
  EmailListResponse,
  SyncResponse,
  ThreadMessage,
  Category,
  EmailCardProps,
  EmailDetailPanelProps,
  EmailListProps,
  UseEmailsResult,
  UseEmailActionsResult,
  UseSyncResult,
  ProviderCount,
  UseProviderCountsResult,
  InboxFolder,
  DraftPayload,
  DraftEmail,
  UseComposeDraftResult,
  UseDraftsResult,
  ComposeMode,
  ComposeState,
  PendingSend,
  UseSendQueueOptions,
  UseSendQueueResult,
  SendToastProps,
} from "./email";

export type {
  ConnectableProvider,
  MailProvider,
  AuthStatus,
  AuthStateByProvider,
  AuthUrl,
  ApiError,
  UseAuthResult,
} from "./auth";

export type {
  InstalledModel,
  LlmStatus,
  CatalogModel,
  DownloadProgress,
  SummarizeResponse,
  UseModelsDataResult,
  UseModelLoaderResult,
  UseModelDownloadResult,
  UseModelDownloadOptions,
} from "./llm";

export type { ButtonVariant, ButtonSize, ButtonProps, BadgeProps, StarButtonProps } from "./ui";
export type { ThemePreference, ResolvedTheme, UseThemeResult } from "./theme";
export type { SidebarProps, ToolbarProps, ComposeActionMode, ComposeActionButtonProps } from "./layout";
