import { useState, useCallback } from "react";
import EmailList from "./EmailList";
import EmailDetailPanel from "./EmailDetailPanel";
import { useEmails } from "./hooks/useEmails";
import { useSync } from "./hooks/useSync";
import { useEmailActions } from "./hooks/useEmailActions";
import { spacing } from "../../styles";
import type { Email, MailProvider } from "../../types";

const DEFAULT_PROVIDER: MailProvider = "all";

export default function InboxPage() {
  const [provider, setProvider] = useState<MailProvider>(DEFAULT_PROVIDER);
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);

  const {
    emails,
    pendingArchive,
    categories,
    loading,
    error: emailsError,
    isAuthenticated,
    loadEmails,
    loadPendingArchive,
    updateEmail,
    removeEmail,
    removePendingArchive,
  } = useEmails(provider);

  const onSyncComplete = useCallback(async () => {
    await loadEmails();
    await loadPendingArchive();
  }, [loadEmails, loadPendingArchive]);

  const { syncing, syncError, sync } = useSync(provider, onSyncComplete);

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
    onEmailUpdate: (id, patch) => {
      updateEmail(id, patch);
      if (selectedEmail?.id === id) {
        setSelectedEmail((prev) => (prev ? { ...prev, ...patch } : prev));
      }
    },
    onEmailRemove: (id) => {
      removeEmail(id);
      if (selectedEmail?.id === id) setSelectedEmail(null);
    },
    onPendingArchiveRemove: removePendingArchive,
    onEmailsReload: loadEmails,
  });

  const handleEmailClick = useCallback(
    (email: Email) => {
      setSelectedEmail(email);
      resetDetail();
      loadThread(email);
    },
    [resetDetail, loadThread],
  );

  const handleProviderChange = useCallback(
    (p: MailProvider) => {
      setSelectedEmail(null);
      setProvider(p);
    },
    [],
  );

  const error = emailsError ?? syncError ?? actionError;

  if (!isAuthenticated) {
    return (
      <div style={{ padding: spacing.page, textAlign: "center" }}>
        <h1>Nadia</h1>
        <p>Veuillez vous connecter à votre boîte mail dans les paramètres.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "calc(100vh - 41px)" }}>
      <EmailList
        emails={emails}
        pendingArchive={pendingArchive}
        categories={categories}
        loading={loading}
        syncing={syncing}
        classifying={classifying}
        error={error}
        provider={provider}
        categoryFilter={categoryFilter}
        onProviderChange={handleProviderChange}
        onCategoryFilterChange={setCategoryFilter}
        onSync={sync}
        onClassifyAll={handleClassifyAll}
        onEmailClick={handleEmailClick}
        onArchive={handleArchive}
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
      />
    </div>
  );
}
