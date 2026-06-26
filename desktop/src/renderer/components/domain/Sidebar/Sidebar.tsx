import "./Sidebar.css";
import { useComputed } from "@preact/signals-react";
import { NavLink } from "react-router-dom";
import { authSignal } from "../../../state";
import {
  IconGear,
  IconChevronDown,
  IconInbox,
  IconSent,
  IconStar,
  IconArchive,
  IconTrash,
  IconTag,
  IconDraft,
} from "../../ui/icons";
import { PROVIDER_LABELS } from "../../../constants/providers";
import { COMING_SOON_LABEL } from "../../../constants/labels";
import type { SidebarProps } from "../../../models/layout";
import type { ConnectableProvider } from "../../../models/auth";
import type { ProviderCount, InboxFolder } from "../../../models/email";

export default function Sidebar({
  activeProvider,
  activeFolder,
  categories,
  categoryFilter,
  providerCounts,
  onProviderSelect,
  onFolderSelect,
  onCategoryFilterChange,
}: SidebarProps) {
  const authByProvider = useComputed(() => authSignal.value).value;
  const connectedProviders = (Object.keys(PROVIDER_LABELS) as ConnectableProvider[]).filter(
    (p) => authByProvider[p]?.is_authenticated,
  );

  return (
    <aside className="sidebar scrollbar-hidden">
      <div className="sidebar__header">
        <h2 className="sidebar__logo">Nadia</h2>
        <NavLink to="/settings" className="sidebar__icon-btn" aria-label="Paramètres">
          <IconGear />
        </NavLink>
      </div>

      <div className="sidebar__accounts">
        {connectedProviders.map((provider) => {
          const isActive = activeProvider === provider;
          const counts = providerCounts[provider];
          return (
            <div key={provider}>
              <button
                type="button"
                className={`sidebar__account${isActive ? " sidebar__account--active" : ""}`}
                onClick={() => onProviderSelect(provider)}
              >
                <IconChevronDown
                  className={`sidebar__account-chevron${isActive ? "" : " sidebar__account-chevron--collapsed"}`}
                />
                <span className="sidebar__account-info">
                  <span className="sidebar__account-name">{PROVIDER_LABELS[provider]}</span>
                  <span className="sidebar__account-email">{authByProvider[provider]?.email}</span>
                </span>
                {!!counts?.totalUnread && (
                  <span className="sidebar__account-badge">{counts.totalUnread}</span>
                )}
              </button>
              {isActive && (
                <SidebarFolders
                  counts={counts}
                  activeFolder={activeFolder}
                  onFolderSelect={onFolderSelect}
                />
              )}
            </div>
          );
        })}
      </div>

      <div className="sidebar__categories">
        <span className="sidebar__categories-title">Catégories Nadia</span>
        <button
          type="button"
          className={`sidebar__category${categoryFilter === "all" ? " sidebar__category--active" : ""}`}
          onClick={() => onCategoryFilterChange("all")}
        >
          <IconTag className="sidebar__category-icon" />
          Toutes
        </button>
        {categories.map((category) => (
          <button
            key={category.id}
            type="button"
            className={`sidebar__category${categoryFilter === category.name ? " sidebar__category--active" : ""}`}
            onClick={() => onCategoryFilterChange(category.name)}
          >
            <IconTag className="sidebar__category-icon" />
            {category.name.charAt(0).toUpperCase() + category.name.slice(1)}
          </button>
        ))}
      </div>
    </aside>
  );
}

function SidebarFolders({
  counts,
  activeFolder,
  onFolderSelect,
}: {
  counts: ProviderCount | undefined;
  activeFolder: InboxFolder;
  onFolderSelect: (folder: InboxFolder) => void;
}) {
  return (
    <nav className="sidebar__folders">
      <button
        type="button"
        className={`sidebar__folder${activeFolder === "inbox" ? " sidebar__folder--current" : ""}`}
        onClick={() => onFolderSelect("inbox")}
      >
        <IconInbox />
        <span className="sidebar__folder-label">Boîte de réception</span>
        <span className="sidebar__folder-count">{counts?.total ?? 0}</span>
      </button>
      <button
        type="button"
        className={`sidebar__folder${activeFolder === "sent" ? " sidebar__folder--current" : ""}`}
        onClick={() => onFolderSelect("sent")}
      >
        <IconSent />
        <span className="sidebar__folder-label">Envoyés</span>
      </button>
      <button
        type="button"
        className={`sidebar__folder${activeFolder === "favoris" ? " sidebar__folder--current" : ""}`}
        onClick={() => onFolderSelect("favoris")}
      >
        <IconStar />
        <span className="sidebar__folder-label">Favoris</span>
        {!!counts?.totalStarred && (
          <span className="sidebar__folder-count">{counts.totalStarred}</span>
        )}
      </button>
      <button
        type="button"
        className={`sidebar__folder${activeFolder === "drafts" ? " sidebar__folder--current" : ""}`}
        onClick={() => onFolderSelect("drafts")}
      >
        <IconDraft />
        <span className="sidebar__folder-label">Brouillons</span>
        {!!counts?.drafts && <span className="sidebar__folder-count">{counts.drafts}</span>}
      </button>
      <span className="sidebar__folder sidebar__folder--disabled" title="Bientôt disponible">
        <IconArchive />
        <span className="sidebar__folder-label">Archivés</span>
      </span>
      <span className="sidebar__folder sidebar__folder--disabled" title={COMING_SOON_LABEL}>
        <IconTrash />
        <span className="sidebar__folder-label">Corbeille</span>
      </span>
    </nav>
  );
}
