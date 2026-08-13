import type { Category } from "../email/Category";
import type { ProviderCount } from "../email/ProviderCount";
import type { InboxFolder } from "../email/InboxFolder";
import type { MailProvider } from "../auth/MailProvider";
import type { ConnectableProvider } from "../auth/ConnectableProvider";

export interface SidebarProps {
  activeProvider: MailProvider;
  activeFolder: InboxFolder;
  categories: Category[];
  categoryFilter: string;
  providerCounts: Partial<Record<ConnectableProvider, ProviderCount>>;
  onProviderSelect: (provider: MailProvider) => void;
  onFolderSelect: (folder: InboxFolder) => void;
  onCategoryFilterChange: (category: string) => void;
}
