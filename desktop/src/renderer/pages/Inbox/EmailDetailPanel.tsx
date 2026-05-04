import Button from "../../components/ui/Button";
import { colors, spacing, radius } from "../../theme";
import type { Email } from "../../types";

interface EmailDetailPanelProps {
  email: Email | null;
  summary: string | null;
  draft: string | null;
  threadCount: number;
  classifying: boolean;
  summarizing: boolean;
  drafting: boolean;
  onClassify: (email: Email) => void;
  onSummarize: (email: Email) => void;
  onSummarizeThread: (email: Email) => void;
  onSuggestReply: (email: Email) => void;
}

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
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: colors.textMuted }}>Sélectionnez un email pour voir les détails</p>
      </div>
    );
  }

  return (
    <div style={{ flex: 1, overflowY: "auto", padding: spacing.page }}>
      <h2>{email.subject || "[Sans objet]"}</h2>

      <div style={{ color: colors.textSecondary, marginBottom: spacing.md }}>
        <div>
          <strong>De :</strong> {email.from_address.name || email.from_address.email}
        </div>
        <div>
          <strong>Date :</strong> {new Date(email.date).toLocaleString("fr-FR")}
        </div>
      </div>

      {/* Actions IA */}
      <div style={{ display: "flex", gap: spacing.sm, marginBottom: spacing.md, flexWrap: "wrap" }}>
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

      {/* Résumé IA */}
      {summary && (
        <div
          style={{
            padding: spacing.card,
            backgroundColor: colors.backgroundMuted,
            borderRadius: radius.sm,
            marginBottom: spacing.md,
            borderLeft: `3px solid ${colors.buttonPrimary}`,
          }}
        >
          <strong style={{ fontSize: "12px", color: colors.textSecondary }}>RÉSUMÉ IA</strong>
          <p style={{ margin: `${spacing.xs}px 0 0`, whiteSpace: "pre-wrap" }}>{summary}</p>
        </div>
      )}

      {/* Brouillon */}
      {(draft ?? email.draft_reply) && (
        <div
          style={{
            padding: spacing.card,
            backgroundColor: colors.backgroundMuted,
            borderRadius: radius.sm,
            marginBottom: spacing.md,
            borderLeft: `3px solid ${colors.textSecondary}`,
          }}
        >
          <strong style={{ fontSize: "12px", color: colors.textSecondary }}>
            BROUILLON DE RÉPONSE
          </strong>
          <p style={{ margin: `${spacing.xs}px 0 0`, whiteSpace: "pre-wrap" }}>
            {draft ?? email.draft_reply}
          </p>
        </div>
      )}

      {/* Corps */}
      <div style={{ marginTop: spacing.page, whiteSpace: "pre-wrap" }}>{email.body_text}</div>
    </div>
  );
}
