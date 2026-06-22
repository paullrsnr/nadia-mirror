import "./InboxPage.css";
import { useState, useEffect, useCallback } from "react";
import Sidebar from "../../components/domain/Sidebar";
import Toolbar from "../../components/domain/Toolbar";
import AuthProviderCard from "../../components/domain/AuthProviderCard";
import ErrorMessage from "../../components/ui/ErrorMessage";
import EmailList from "./EmailList";
import EmailDetailPanel from "./EmailDetailPanel";
import { useEmails } from "./hooks/useEmails";
import { useSync } from "./hooks/useSync";
import { useEmailActions } from "./hooks/useEmailActions";
import { useProviderCounts } from "./hooks/useProviderCounts";
import { useTheme } from "../../hooks/useTheme";
import { useAuth } from "../../hooks/useAuth";
import { starEmail, markEmailRead } from "../../services/api/emails.api";
import type { Email, MailProvider, ConnectableProvider, InboxFolder } from "../../models";

const PROVIDER_LABELS: Record<ConnectableProvider, string> = {
  gmail: "Gmail",
  outlook: "Outlook",
};

export default function InboxPage() {
  const [provider, setProvider] = useState<MailProvider>("all");
  const [folder, setFolder] = useState<InboxFolder>("inbox");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [searchValue, setSearchValue] = useState("");
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const { theme, toggle } = useTheme();
  const {
    authByProvider,
    loading: authLoading,
    error: authError,
    providers: connectableProviders,
    connect,
    disconnect,
  } = useAuth();
  const { providerCounts, refreshProviderCounts } = useProviderCounts();

  // Sélectionne automatiquement le premier compte connecté (la Sidebar n'a pas
  // de vue "toutes les boîtes" — elle reflète exactement les comptes Figma).
  useEffect(() => {
    if (provider !== "all") return;
    const firstConnected = connectableProviders.find((p) => authByProvider[p]?.is_authenticated);
    if (firstConnected) setProvider(firstConnected);
  }, [provider, connectableProviders, authByProvider]);

  const {
    emails,
    pendingArchive,
    categories,
    loading,
    error: emailsError,
    isAuthenticated,
    loadEmails,
    loadAll,
    removeEmail,
    removePendingArchive,
    setEmailStarred,
    setEmailRead,
  } = useEmails(provider);

  // Synchronise l'email sélectionné quand la liste se recharge (ex: après classify)
  useEffect(() => {
    setSelectedEmail((prev) => {
      if (!prev) return prev;
      return emails.find((e) => e.id === prev.id) ?? prev;
    });
  }, [emails]);

  const { syncing, syncError, sync } = useSync(provider, async () => {
    await loadAll();
    refreshProviderCounts();
  });

  const {
    classifying,
    summarizing,
    drafting,
    summary,
    draft,
    threadCount,
    actionError,
    resetDetail,
    loadThread,
    handleClassify,
    handleClassifyAll,
    handleSummarize,
    handleSummarizeThread,
    handleSuggestReply,
    handleArchive,
    handleConfirmArchive,
    handleRejectArchive,
  } = useEmailActions({
    provider,
    onEmailRemove: (id) => {
      removeEmail(id);
      if (selectedEmail?.id === id) setSelectedEmail(null);
      refreshProviderCounts();
    },
    onPendingArchiveRemove: removePendingArchive,
    onEmailsReload: loadEmails,
  });

  const handleEmailClick = useCallback(
    (email: Email) => {
      setSelectedEmail(email);
      resetDetail();
      loadThread(email);
      handleSuggestReply(email);

      if (email.labels.includes("UNREAD")) {
        const readProvider = provider === "all" ? (email.provider ?? "gmail") : provider;
        setEmailRead(email.id);
        if (readProvider !== "all") {
          markEmailRead(email.id, readProvider as MailProvider)
            .then(refreshProviderCounts)
            .catch(() => {});
        }
      }
    },
    [provider, resetDetail, loadThread, handleSuggestReply, setEmailRead, refreshProviderCounts],
  );

  const handleProviderChange = useCallback((p: MailProvider) => {
    setSelectedEmail(null);
    setFolder("inbox");
    setProvider(p);
  }, []);

  const handleFolderSelect = useCallback((f: InboxFolder) => {
    setSelectedEmail(null);
    setFolder(f);
  }, []);

  const handleToggleStar = useCallback(
    (email: Email) => {
      const next = !email.is_starred;
      setEmailStarred(email.id, next);
      starEmail(email.id, next)
        .then(refreshProviderCounts)
        .catch(() => setEmailStarred(email.id, !next));
    },
    [setEmailStarred, refreshProviderCounts],
  );

  const error = emailsError ?? syncError ?? actionError;

  if (!isAuthenticated) {
    return (
      <div className="inbox-unauthenticated">
        <h1 className="inbox-unauthenticated__title">Nadia</h1>
        <p className="inbox-unauthenticated__desc">
          Connectez une boîte mail pour commencer.
        </p>
        {authError && <ErrorMessage message={authError} />}
        <div className="inbox-unauthenticated__cards">
          {connectableProviders.map((p) => (
            <AuthProviderCard
              key={p}
              provider={p}
              label={PROVIDER_LABELS[p]}
              status={authByProvider[p]}
              loading={authLoading[p]}
              onConnect={() => connect(p)}
              onDisconnect={() => disconnect(p)}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="inbox-shell">
      <Toolbar
        searchValue={searchValue}
        onSearchChange={setSearchValue}
        theme={theme}
        onToggleTheme={toggle}
      />
      <div className="inbox-layout">
        <Sidebar
          activeProvider={provider}
          activeFolder={folder}
          categories={categories}
          categoryFilter={categoryFilter}
          providerCounts={providerCounts}
          onProviderSelect={handleProviderChange}
          onFolderSelect={handleFolderSelect}
          onCategoryFilterChange={setCategoryFilter}
        />
        <EmailList
          emails={emails}
          pendingArchive={pendingArchive}
          loading={loading}
          syncing={syncing}
          classifying={classifying}
          error={error}
          provider={provider}
          folder={folder}
          categoryFilter={categoryFilter}
          searchValue={searchValue}
          selectedEmailId={selectedEmail?.id ?? null}
          onSync={sync}
          onClassifyAll={handleClassifyAll}
          onEmailClick={handleEmailClick}
          onArchive={handleArchive}
          onToggleStar={handleToggleStar}
          onConfirmArchive={handleConfirmArchive}
          onRejectArchive={handleRejectArchive}
        />
        <EmailDetailPanel
          email={selectedEmail}
          summary={summary}
          draft={draft}
          threadCount={threadCount}
          classifying={classifying}
          summarizing={summarizing}
          drafting={drafting}
          onClassify={handleClassify}
          onSummarize={handleSummarize}
          onSummarizeThread={handleSummarizeThread}
          onSuggestReply={handleSuggestReply}
          onToggleStar={handleToggleStar}
        />
      </div>
    </div>
  );
}
