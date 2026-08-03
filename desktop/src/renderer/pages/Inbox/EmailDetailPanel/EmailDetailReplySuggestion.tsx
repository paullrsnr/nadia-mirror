import "./EmailDetailReplySuggestion.css";
import { IconSparkles } from "../../../components/ui/icons";
import type { EmailDetailReplySuggestionProps } from "../../../models/email";
import { extractReplyHeadline } from "../../../helpers";

const NO_REPLY_NEEDED = "Cet email ne semble pas nécessiter de réponse.";

export default function EmailDetailReplySuggestion({
  summary,
  draft,
  draftReply,
  drafting,
}: EmailDetailReplySuggestionProps) {
  const reply = draft ?? draftReply;
  if (!summary && !reply && !drafting) return null;

  return (
    <div className="email-detail-reply-suggestion">
      <div className="email-detail-reply-suggestion__title">
        <IconSparkles />
        Suggestions de Nadia
      </div>

      {summary && (
        <div className="email-detail-reply-suggestion__ai-box">
          <strong className="email-detail-reply-suggestion__ai-label">RÉSUMÉ IA</strong>
          <p className="email-detail-reply-suggestion__ai-body">{summary}</p>
        </div>
      )}

      {drafting && (
        <div className="email-detail-reply-suggestion__pill email-detail-reply-suggestion__pill--loading">
          Génération de la réponse...
        </div>
      )}

      {!drafting &&
        reply &&
        (reply === NO_REPLY_NEEDED ? (
          <p className="email-detail-reply-suggestion__ai-body">{reply}</p>
        ) : (
          <div className="email-detail-reply-suggestion__pills">
            <button type="button" className="email-detail-reply-suggestion__pill">
              {extractReplyHeadline(reply)}
            </button>
          </div>
        ))}
    </div>
  );
}
