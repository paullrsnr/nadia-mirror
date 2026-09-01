import "./EmailDetailHeader.css";
import { useState } from "react";
import {
  IconSparkles,
  IconStar,
  IconReply,
  IconForward,
  IconArchive,
  IconTrash,
  IconMoreHorizontal,
} from "../../../components/ui/icons";
import type { EmailDetailHeaderProps } from "../../../models/email";
import { getStarTitle } from "../../../constants/labels";

export default function EmailDetailHeader({
  email,
  threadCount,
  classifying,
  summarizing,
  drafting,
  nadiaOpen,
  onToggleNadia,
  onClassify,
  onSummarize,
  onSummarizeThread,
  onSuggestReply,
  onToggleStar,
  onReply,
  onForward,
}: EmailDetailHeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="email-detail-header">
      <div className="email-detail-header__top">
        <div className="email-detail-header__title-block">
          <h2 className="email-detail-header__subject">{email.subject || "[Sans objet]"}</h2>
          <div className="email-detail-header__meta">
            {email.from_address.name || email.from_address.email}
            {email.from_address.name && (
              <span className="email-detail-header__meta-email"> &lt;{email.from_address.email}&gt;</span>
            )}
          </div>
          <div className="email-detail-header__date">{new Date(email.date).toLocaleString("fr-FR")}</div>
        </div>

        <div className="email-detail-header__icon-actions">
          <button
            type="button"
            className={`email-detail-header__icon-btn${email.is_starred ? " email-detail-header__icon-btn--star-active" : ""}`}
            title={getStarTitle(email.is_starred ?? false)}
            onClick={() => onToggleStar(email)}
          >
            <IconStar filled={email.is_starred} />
          </button>
          <button
            type="button"
            className="email-detail-header__icon-btn"
            title="Répondre"
            onClick={() => onReply(email)}
          >
            <IconReply />
          </button>
          <button
            type="button"
            className="email-detail-header__icon-btn"
            title="Transférer"
            onClick={() => onForward(email)}
          >
            <IconForward />
          </button>
          <button type="button" className="email-detail-header__icon-btn" title="Archiver">
            <IconArchive />
          </button>
          <button type="button" className="email-detail-header__icon-btn" title="Supprimer">
            <IconTrash />
          </button>
          <div className="email-detail-header__menu-wrap">
            <button
              type="button"
              className="email-detail-header__icon-btn"
              title="Plus d'actions IA"
              onClick={() => setMenuOpen((o) => !o)}
            >
              <IconMoreHorizontal />
            </button>
            {menuOpen && (
              <>
                <div className="email-detail-header__menu-backdrop" onClick={() => setMenuOpen(false)} />
                <div className="email-detail-header__menu">
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

      <button type="button" className="email-detail-header__nadia-cta" onClick={onToggleNadia}>
        <IconSparkles />
        {nadiaOpen ? "Masquer Nadia" : "Discuter avec Nadia"}
      </button>
    </div>
  );
}
