import "./EmailDetailReplySuggestion.css";
import { IconSparkles } from "../../../components/ui/icons";
import type { EmailDetailReplySuggestionProps } from "../../../models/email";

const GREETING_PATTERN = /^(bonjour|cher|chère|madame|monsieur|salut|hello|hi)\b/i;
const SIGNOFF_PATTERN = /^(cordialement|bien à vous|bonne journée|bonne soirée|merci|à bientôt|sincèrement|amicalement)\b/i;
const SIGNATURE_NAME_PATTERN = /^[A-ZÀ-Ý][\wà-ÿ'-]*(\s+[A-ZÀ-Ý][\wà-ÿ'-]*){0,2}$/;
const NO_REPLY_NEEDED = "Cet email ne semble pas nécessiter de réponse.";

function extractReplyHeadline(text: string): string {
  const lines = text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const coreLine =
    lines.find(
      (line) =>
        !GREETING_PATTERN.test(line) &&
        !SIGNOFF_PATTERN.test(line) &&
        !SIGNATURE_NAME_PATTERN.test(line),
    ) ?? lines[0] ?? text;

  const firstSentence = coreLine.split(/(?<=[.!?])\s/)[0].trim();
  return firstSentence.length > 100 ? `${firstSentence.slice(0, 97)}…` : firstSentence;
}

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
