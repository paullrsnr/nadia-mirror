import "./EmailDetailPanel.css";
import Button from "../../components/ui/Button";
import type { EmailDetailPanelProps } from "../../models/email";

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
}: EmailDetailPanelProps) {
  if (!email) {
    return (
      <div className="email-detail__empty">
        <p className="email-detail__empty-text">
          Sélectionnez un email pour voir les détails
        </p>
      </div>
    );
  }

  return (
    <div className="email-detail">
      <h2>{email.subject || "[Sans objet]"}</h2>

      <div className="email-detail__meta">
        <div><strong>De :</strong> {email.from_address.name || email.from_address.email}</div>
        <div><strong>Date :</strong> {new Date(email.date).toLocaleString("fr-FR")}</div>
      </div>

      <div className="email-detail__actions">
        <Button
          variant="secondary"
          onClick={() => onClassify(email)}
          disabled={classifying || summarizing}
        >
          {classifying
            ? "Classification..."
            : email.category
              ? `Catégorie : ${email.category}`
              : "Classifier avec l'IA"}
        </Button>

        <Button onClick={() => onSummarize(email)} disabled={summarizing}>
          {summarizing ? "Résumé en cours..." : "Résumer avec l'IA"}
        </Button>

        {threadCount > 1 && (
          <Button onClick={() => onSummarizeThread(email)} disabled={summarizing}>
            {summarizing
              ? "Résumé en cours..."
              : `Résumer la discussion (${threadCount} messages)`}
          </Button>
        )}

        <Button
          variant="secondary"
          onClick={() => onSuggestReply(email)}
          disabled={drafting || summarizing}
        >
          {drafting ? "Analyse en cours..." : "Suggérer une réponse (IA)"}
        </Button>
      </div>

      {summary && (
        <div className="email-detail__ai-box">
          <strong className="email-detail__ai-label">RÉSUMÉ IA</strong>
          <p className="email-detail__ai-body">{summary}</p>
        </div>
      )}

      {(draft ?? email.draft_reply) && (
        <div className="email-detail__ai-box email-detail__ai-box--draft">
          <strong className="email-detail__ai-label">BROUILLON DE RÉPONSE</strong>
          <p className="email-detail__ai-body">{draft ?? email.draft_reply}</p>
        </div>
      )}

      <div className="email-detail__body">{email.body_text}</div>
    </div>
  );
}
