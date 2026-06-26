import "./EmailDetailPanel.css";
import { useEffect, useRef, useState } from "react";
import {
  IconSparkles,
  IconStar,
  IconReply,
  IconForward,
  IconArchive,
  IconTrash,
  IconMoreHorizontal,
  IconSend,
  IconAttachment,
  IconDownload,
} from "../../components/ui/icons";
import type { EmailDetailPanelProps } from "../../models/email";
import { getAttachmentDownloadUrl } from "../../services/api/emails.api";
import EmailHtmlBody, { isRichHtml } from "../../components/domain/EmailHtmlBody";

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
}

const GREETING_PATTERN = /^(bonjour|cher|chère|madame|monsieur|salut|hello|hi)\b/i;
const SIGNOFF_PATTERN = /^(cordialement|bien à vous|bonne journée|bonne soirée|merci|à bientôt|sincèrement|amicalement)\b/i;
const SIGNATURE_NAME_PATTERN = /^[A-ZÀ-Ý][\wà-ÿ'-]*(\s+[A-ZÀ-Ý][\wà-ÿ'-]*){0,2}$/;

const SCROLL_INDICATOR_TIMEOUT_MS = 800;

function extractReplyHeadline(draft: string): string {
  const lines = draft
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const coreLine =
    lines.find(
      (line) =>
        !GREETING_PATTERN.test(line) &&
        !SIGNOFF_PATTERN.test(line) &&
        !SIGNATURE_NAME_PATTERN.test(line),
    ) ?? lines[0] ?? draft;

  const firstSentence = coreLine.split(/(?<=[.!?])\s/)[0].trim();
  return firstSentence.length > 100 ? `${firstSentence.slice(0, 97)}…` : firstSentence;
}

export default function EmailDetailPanel({
  email,
  folder,
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
  onReply,
  onForward,
}: EmailDetailPanelProps) {
  const [nadiaOpen, setNadiaOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const contentRef = useRef<HTMLDivElement>(null);
  const scrollTimeout = useRef<number | undefined>(undefined);

  useEffect(() => {
    setNadiaOpen(false);
    setMenuOpen(false);
    setChatInput("");
  }, [email?.id]);

  function handleContentScroll() {
    contentRef.current?.classList.add("is-scrolling");
    window.clearTimeout(scrollTimeout.current);
    scrollTimeout.current = window.setTimeout(() => {
      contentRef.current?.classList.remove("is-scrolling");
    }, SCROLL_INDICATOR_TIMEOUT_MS);
  }

  if (!email) {
    return (
      <div className="email-detail email-detail--empty">
        <p className="email-detail__empty-text">Sélectionnez un email pour voir les détails</p>
      </div>
    );
  }

  return (
    <div className="email-detail">
      <div className="email-detail__header">
        <div className="email-detail__header-top">
          <div className="email-detail__title-block">
            <h2 className="email-detail__subject">{email.subject || "[Sans objet]"}</h2>
            <div className="email-detail__meta">
              {email.from_address.name || email.from_address.email}
              {email.from_address.name && (
                <span className="email-detail__meta-email"> &lt;{email.from_address.email}&gt;</span>
              )}
            </div>
            <div className="email-detail__date">{new Date(email.date).toLocaleString("fr-FR")}</div>
          </div>

          <div className="email-detail__icon-actions">
            <button
              type="button"
              className={`email-detail__icon-btn${email.is_starred ? " email-detail__icon-btn--star-active" : ""}`}
              title={email.is_starred ? "Retirer des favoris" : "Ajouter aux favoris"}
              onClick={() => onToggleStar(email)}
            >
              <IconStar filled={email.is_starred} />
            </button>
            <button type="button" className="email-detail__icon-btn" title="Répondre" onClick={() => onReply(email)}>
              <IconReply />
            </button>
            <button type="button" className="email-detail__icon-btn" title="Transférer" onClick={() => onForward(email)}>
              <IconForward />
            </button>
            <button type="button" className="email-detail__icon-btn" title="Archiver">
              <IconArchive />
            </button>
            <button type="button" className="email-detail__icon-btn" title="Supprimer">
              <IconTrash />
            </button>
            <div className="email-detail__menu-wrap">
              <button
                type="button"
                className="email-detail__icon-btn"
                title="Plus d'actions IA"
                onClick={() => setMenuOpen((o) => !o)}
              >
                <IconMoreHorizontal />
              </button>
              {menuOpen && (
                <>
                  <div className="email-detail__menu-backdrop" onClick={() => setMenuOpen(false)} />
                  <div className="email-detail__menu">
                    <button
                      type="button"
                      onClick={() => {
                        onClassify(email);
                        setMenuOpen(false);
                      }}
                      disabled={classifying || summarizing}
                    >
                      {email.category ? `Catégorie : ${email.category}` : "Classifier avec l'IA"}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        onSummarize(email);
                        setMenuOpen(false);
                      }}
                      disabled={summarizing}
                    >
                      Résumer avec l'IA
                    </button>
                    {threadCount > 1 && (
                      <button
                        type="button"
                        onClick={() => {
                          onSummarizeThread(email);
                          setMenuOpen(false);
                        }}
                        disabled={summarizing}
                      >
                        Résumer la discussion ({threadCount} messages)
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => {
                        onSuggestReply(email);
                        setMenuOpen(false);
                      }}
                      disabled={drafting || summarizing}
                    >
                      Suggérer une réponse (IA)
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        <button
          type="button"
          className="email-detail__nadia-cta"
          onClick={() => setNadiaOpen((o) => !o)}
        >
          <IconSparkles />
          {nadiaOpen ? "Masquer Nadia" : "Discuter avec Nadia"}
        </button>
      </div>

      {nadiaOpen ? (
        <div className="email-detail__nadia-chat">
          <div className="email-detail__nadia-empty">
            <div className="email-detail__nadia-icon">
              <IconSparkles />
            </div>
            <h3 className="email-detail__nadia-title">Bonjour, je suis Nadia</h3>
            <p className="email-detail__nadia-desc">
              Comment puis-je vous aider avec cet email ? Je peux le catégoriser, l'archiver ou vous
              proposer des réponses.
            </p>
          </div>
          <div className="email-detail__nadia-input-row">
            <input
              type="text"
              className="email-detail__nadia-input"
              placeholder="Posez votre question à Nadia..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <button type="button" className="email-detail__nadia-send" disabled={!chatInput.trim()}>
              <IconSend />
            </button>
          </div>
        </div>
      ) : (
        <div className="email-detail__content" ref={contentRef} onScroll={handleContentScroll}>
          {email.body_html && isRichHtml(email.body_html) ? (
            <div className="email-detail__body email-detail__body--html">
              <EmailHtmlBody html={email.body_html} />
            </div>
          ) : (
            <div className="email-detail__body">{email.body_text}</div>
          )}

          {email.attachments.length > 0 && (
            <div className="email-detail__attachments">
              <div className="email-detail__attachments-title">
                <IconAttachment />
                {email.attachments.length} pièce{email.attachments.length > 1 ? "s" : ""} jointe
                {email.attachments.length > 1 ? "s" : ""}
              </div>
              <ul className="email-detail__attachments-list">
                {email.attachments.map((attachment) => (
                  <li key={attachment.attachment_id} className="email-detail__attachment">
                    <span className="email-detail__attachment-name">{attachment.filename}</span>
                    <span className="email-detail__attachment-size">{formatFileSize(attachment.size)}</span>
                    <a
                      className="email-detail__attachment-download"
                      href={getAttachmentDownloadUrl(email.id, attachment.attachment_id)}
                      download={attachment.filename}
                      title="Télécharger"
                    >
                      <IconDownload />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {folder !== "sent" && (summary || draft || email.draft_reply || drafting) && (
            <div className="email-detail__suggestions">
              <div className="email-detail__suggestions-title">
                <IconSparkles />
                Suggestions de Nadia
              </div>

              {summary && (
                <div className="email-detail__ai-box">
                  <strong className="email-detail__ai-label">RÉSUMÉ IA</strong>
                  <p className="email-detail__ai-body">{summary}</p>
                </div>
              )}

              {drafting && (
                <div className="email-detail__reply-pill email-detail__reply-pill--loading">
                  Génération de la réponse...
                </div>
              )}

              {!drafting && (draft ?? email.draft_reply) && (
                (draft ?? email.draft_reply) === "Cet email ne semble pas nécessiter de réponse." ? (
                  <p className="email-detail__ai-body">{draft ?? email.draft_reply}</p>
                ) : (
                  <div className="email-detail__reply-suggestions">
                    <button type="button" className="email-detail__reply-pill">
                      {extractReplyHeadline(draft ?? email.draft_reply ?? "")}
                    </button>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
