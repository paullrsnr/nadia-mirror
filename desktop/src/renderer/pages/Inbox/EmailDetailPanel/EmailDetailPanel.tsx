import "./EmailDetailPanel.css";
import { useEffect, useState } from "react";
import type { EmailDetailPanelProps } from "../../../models/email";
import EmailDetailHeader from "./EmailDetailHeader";
import EmailDetailBody from "./EmailDetailBody";
import EmailDetailAttachments from "./EmailDetailAttachments";
import EmailDetailReplySuggestion from "./EmailDetailReplySuggestion";
import EmailDetailNadiaChat from "./EmailDetailNadiaChat";

export default function EmailDetailPanel({
  email,
  summary,
  draft,
  threadCount,
  classifying,
  summarizing,
  drafting,
  onClassify,
  onSummarize,
  onSummarizeThread,
  onSuggestReply,
  onToggleStar,
}: EmailDetailPanelProps) {
  const [nadiaOpen, setNadiaOpen] = useState(false);

  useEffect(() => {
    setNadiaOpen(false);
  }, [email?.id]);

  if (!email) {
    return (
      <div className="email-detail email-detail--empty">
        <p className="email-detail__empty-text">Sélectionnez un email pour voir les détails</p>
      </div>
    );
  }

  return (
    <div className="email-detail">
      <EmailDetailHeader
        email={email}
        threadCount={threadCount}
        classifying={classifying}
        summarizing={summarizing}
        drafting={drafting}
        nadiaOpen={nadiaOpen}
        onToggleNadia={() => setNadiaOpen((o) => !o)}
        onClassify={onClassify}
        onSummarize={onSummarize}
        onSummarizeThread={onSummarizeThread}
        onSuggestReply={onSuggestReply}
        onToggleStar={onToggleStar}
      />

      {nadiaOpen ? (
        <EmailDetailNadiaChat />
      ) : (
        <div className="email-detail__content scrollbar-hidden">
          <EmailDetailBody email={email} />
          <EmailDetailAttachments emailId={email.id} attachments={email.attachments} />
          <EmailDetailReplySuggestion
            summary={summary}
            draft={draft}
            draftReply={email.draft_reply ?? null}
            drafting={drafting}
          />
        </div>
      )}
    </div>
  );
}
