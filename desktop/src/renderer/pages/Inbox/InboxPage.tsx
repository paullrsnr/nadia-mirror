import "./InboxPage.css";
import { useState, useEffect, useCallback } from "react";
import Sidebar from "../../components/domain/Sidebar";
import Toolbar from "../../components/domain/Toolbar";
import AuthProviderCard from "../../components/domain/AuthProviderCard";
import ErrorMessage from "../../components/ui/ErrorMessage";
import EmailList from "./EmailList";
import EmailDetailPanel from "./EmailDetailPanel";
import ComposeModal from "./ComposeModal";
import DraftsList from "./DraftsList";
import SendToast from "./SendToast";
import { useEmails } from "./hooks/useEmails";
import { useSync } from "./hooks/useSync";
import { useEmailActions } from "./hooks/useEmailActions";
import { useProviderCounts } from "./hooks/useProviderCounts";
import { useDrafts } from "./hooks/useDrafts";
import { useSendQueue } from "./hooks/useSendQueue";
import { useTheme } from "../../hooks/useTheme";
import { useAuth } from "../../hooks/useAuth";
import { starEmail, markEmailRead } from "../../services/api/emails.api";
import { PROVIDER_LABELS } from "../../constants/providers";
import { UNREAD_LABEL } from "../../constants/labels";
import { deleteDraft } from "../../services/api/drafts.api";
import type { DraftEmail, Email, MailProvider, InboxFolder, ComposeState } from "../../models";

export default function InboxPage() {
  const [provider, setProvider] = useState<MailProvider>("all");
  const [folder, setFolder] = useState<InboxFolder>("inbox");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [searchValue, setSearchValue] = useState("");
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [markReadError, setMarkReadError] = useState<string | null>(null);
  const { themePreference, cycleTheme } = useTheme();
  const [composeState, setComposeState] = useState<ComposeState | null>(null);
  const {
    authByProvider,
    loading: authLoading,
    error: authError,
    providers: connectableProviders,
    connect,
    disconnect,
  } = useAuth();
  const { providerCounts, refreshProviderCounts } = useProviderCounts();

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
  } = useEmails(provider, folder);

  const { drafts, loading: draftsLoading, error: draftsError, loadDrafts, removeDraft } = useDrafts(provider);

  useEffect(() => {
    if (folder === "drafts") loadDrafts();
  }, [folder, loadDrafts]);

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

      if (email.labels.includes(UNREAD_LABEL)) {
        const readProvider = provider === "all" ? email.provider : provider;
        setMarkReadError(null);
        setEmailRead(email.id, true);
        if (readProvider) {
          markEmailRead(email.id, readProvider as MailProvider)
            .then(refreshProviderCounts)
            .catch(() => {
              setEmailRead(email.id, false);
              setMarkReadError("Erreur lors du marquage comme lu");
            });
        } else {
          console.error(`Email ${email.id} sans provider connu — marquage "lu" non synchronisé avec le serveur`);
        }
      }
    },
    [provider, resetDetail, loadThread, handleSuggestReply, setEmailRead, refreshProviderCounts],
  );

  const handleComposeClick = useCallback(() => {
    setComposeState({ open: true, mode: "new" });
  }, []);

  const handleReply = useCallback((email: Email) => {
    setComposeState({ open: true, mode: "reply", replyTo: email });
  }, []);

  const handleForward = useCallback((email: Email) => {
    setComposeState({ open: true, mode: "forward", replyTo: email });
  }, []);

  const handleOpenDraft = useCallback((draft: DraftEmail) => {
    setComposeState({ open: true, mode: "draft", draft });
  }, []);

  const handleDeleteDraft = useCallback(
    (draft: DraftEmail) => {
      removeDraft(draft.id);
      deleteDraft(draft.id)
        .then(refreshProviderCounts)
        .catch(() => loadDrafts());
    },
    [removeDraft, loadDrafts, refreshProviderCounts],
  );

  const refreshCurrentFolder = useCallback(() => {
    refreshProviderCounts();
    if (folder === "drafts") loadDrafts();
    if (folder === "sent") loadEmails();
  }, [folder, loadDrafts, loadEmails, refreshProviderCounts]);

  const { pendingSend, requestSend, cancelSend } = useSendQueue({
    onSendComplete: refreshCurrentFolder,
  });

  const handleComposeClose = useCallback(() => {
    setComposeState(null);
    refreshCurrentFolder();
  }, [refreshCurrentFolder]);

  const handleSendRequested = useCallback(
    (draftId: string, subject: string) => {
      setComposeState(null);
      if (folder === "drafts") loadDrafts();
      requestSend(draftId, subject);
    },
    [folder, loadDrafts, requestSend],
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

  const error = emailsError ?? syncError ?? actionError ?? markReadError;

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
        themePreference={themePreference}
        onCycleTheme={cycleTheme}
        onComposeClick={handleComposeClick}
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
        {folder === "drafts" ? (
          <DraftsList
            drafts={drafts}
            loading={draftsLoading}
            error={draftsError}
            onDraftClick={handleOpenDraft}
            onDraftDelete={handleDeleteDraft}
          />
        ) : (
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
        )}
        {folder !== "drafts" && (
          <EmailDetailPanel
            email={selectedEmail}
            folder={folder}
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
            onReply={handleReply}
            onForward={handleForward}
          />
        )}
      </div>
      {composeState?.open && (
        <ComposeModal
          provider={
            composeState.draft
              ? (composeState.draft.provider as MailProvider)
              : composeState.replyTo
                ? ((composeState.replyTo.provider ?? "gmail") as MailProvider)
                : provider === "all"
                  ? "gmail"
                  : provider
          }
          mode={composeState.mode}
          replyTo={composeState.replyTo}
          existingDraft={composeState.draft}
          onClose={handleComposeClose}
          onSendRequested={handleSendRequested}
        />
      )}
      {pendingSend && <SendToast subject={pendingSend.subject} onCancel={cancelSend} />}
    </div>
  );
}
