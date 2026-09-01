import "./ComposeModal.css";
import { useEffect, useRef, useState } from "react";
import Button from "../../components/ui/Button";
import ErrorMessage from "../../components/ui/ErrorMessage";
import ComposeActionButton from "../../components/domain/ComposeActionButton";
import { IconExpand, IconCompress, IconAttachment, IconLink } from "../../components/ui/icons";
import { useComposeDraft } from "./hooks/useComposeDraft";
import ComposeToolbar from "./ComposeToolbar";
import type { ComposeMode, ComposeModalProps } from "../../models";
import { formatFileSize } from "../../helpers";

const SCROLL_INDICATOR_TIMEOUT_MS = 800;

const MODE_TITLES: Record<ComposeMode, string> = {
  new: "Nouveau message",
  reply: "Répondre",
  forward: "Transférer",
  draft: "Brouillon",
};

export default function ComposeModal({ provider, mode, replyTo, existingDraft, onClose, onSendRequested }: ComposeModalProps) {
  const [expanded, setExpanded] = useState(false);
  const [linkOpen, setLinkOpen] = useState(false);
  const [linkUrl, setLinkUrl] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const bodyScrollTimeout = useRef<number | undefined>(undefined);
  const {
    to,
    cc,
    bcc,
    subject,
    bodyRef,
    initialBodyHtml,
    setTo,
    setCc,
    setBcc,
    setSubject,
    handleBodyInput,
    saving,
    sending,
    sendError,
    attachments,
    uploadingAttachment,
    handleAddAttachments,
    handleRemoveAttachment,
    ccVisible,
    bccVisible,
    showCc,
    showBcc,
    execFormat,
    resetTextColor,
    toggleHighlight,
    resetHighlight,
    handleSend,
  } = useComposeDraft({
    provider,
    mode,
    replyTo,
    existingDraft,
    onSent: onSendRequested,
  });

  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.innerHTML = initialBodyHtml;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleInsertLink() {
    const url = linkUrl.trim();
    if (url) execFormat("createLink", url);
    setLinkUrl("");
    setLinkOpen(false);
  }

  function handleBodyScroll() {
    bodyRef.current?.classList.add("is-scrolling");
    window.clearTimeout(bodyScrollTimeout.current);
    bodyScrollTimeout.current = window.setTimeout(() => {
      bodyRef.current?.classList.remove("is-scrolling");
    }, SCROLL_INDICATOR_TIMEOUT_MS);
  }

  return (
    <>
      <div className="compose-modal__backdrop" onClick={onClose} />
      <div className={`compose-modal${expanded ? " compose-modal--expanded" : ""}`}>
        <div className="compose-modal__header">
          <h2 className="compose-modal__title">{MODE_TITLES[mode]}</h2>
          <div className="compose-modal__header-actions">
            <button
              type="button"
              className="compose-modal__icon-btn"
              onClick={() => setExpanded((e) => !e)}
              aria-label={expanded ? "Réduire" : "Agrandir"}
              title={expanded ? "Réduire" : "Agrandir"}
            >
              {expanded ? <IconCompress /> : <IconExpand />}
            </button>
            <button type="button" className="compose-modal__close" onClick={onClose} aria-label="Fermer">
              ×
            </button>
          </div>
        </div>

        <div className="compose-modal__field">
          <label htmlFor="compose-to">À</label>
          <input
            id="compose-to"
            type="text"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            placeholder="destinataire@exemple.com"
          />
          <div className="compose-modal__field-toggles">
            {!ccVisible && (
              <button type="button" className="compose-modal__field-toggle" onClick={showCc}>
                Cc
              </button>
            )}
            {!bccVisible && (
              <button type="button" className="compose-modal__field-toggle" onClick={showBcc}>
                Cci
              </button>
            )}
          </div>
        </div>
        {ccVisible && (
          <div className="compose-modal__field">
            <label htmlFor="compose-cc">Cc</label>
            <input id="compose-cc" type="text" value={cc} onChange={(e) => setCc(e.target.value)} />
          </div>
        )}
        {bccVisible && (
          <div className="compose-modal__field">
            <label htmlFor="compose-bcc">Cci</label>
            <input id="compose-bcc" type="text" value={bcc} onChange={(e) => setBcc(e.target.value)} />
          </div>
        )}
        <div className="compose-modal__field">
          <label htmlFor="compose-subject">Objet</label>
          <input
            id="compose-subject"
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
        </div>

        <ComposeToolbar
          execFormat={execFormat}
          resetTextColor={resetTextColor}
          toggleHighlight={toggleHighlight}
          resetHighlight={resetHighlight}
        />

        <div
          ref={bodyRef}
          className="compose-modal__body"
          contentEditable
          suppressContentEditableWarning
          onInput={handleBodyInput}
          onScroll={handleBodyScroll}
          data-placeholder="Rédigez votre message..."
        />

        {attachments.length > 0 && (
          <ul className="compose-modal__attachments">
            {attachments.map((attachment) => (
              <li key={attachment.attachment_id} className="compose-modal__attachment">
                <span className="compose-modal__attachment-name">{attachment.filename}</span>
                <span className="compose-modal__attachment-size">{formatFileSize(attachment.size)}</span>
                <button
                  type="button"
                  className="compose-modal__attachment-remove"
                  onClick={() => handleRemoveAttachment(attachment.attachment_id)}
                  aria-label="Supprimer la pièce jointe"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}

        {sendError && <ErrorMessage message={sendError} />}

        <div className="compose-modal__footer">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            hidden
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                handleAddAttachments(e.target.files);
              }
              e.target.value = "";
            }}
          />
          <div className="compose-modal__footer-left">
            <ComposeActionButton mode="send" disabled={sending || !to.trim()} onClick={handleSend} />
            <button
              type="button"
              className="compose-modal__icon-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingAttachment}
              aria-label="Joindre un fichier"
              title="Joindre un fichier"
            >
              <IconAttachment />
            </button>
            <div className="compose-modal__popover-wrap">
              <button
                type="button"
                className="compose-modal__icon-btn"
                onClick={() => setLinkOpen((o) => !o)}
                aria-label="Insérer un lien"
                title="Insérer un lien"
              >
                <IconLink />
              </button>
              {linkOpen && (
                <div className="compose-modal__link-popover">
                  <input
                    type="text"
                    placeholder="https://exemple.com"
                    value={linkUrl}
                    onChange={(e) => setLinkUrl(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleInsertLink()}
                  />
                  <Button size="sm" variant="primary" onClick={handleInsertLink}>
                    Insérer
                  </Button>
                </div>
              )}
            </div>
          </div>
          <span className="compose-modal__saving-status">
            {saving ? "Enregistrement..." : "Brouillon enregistré"}
          </span>
        </div>
      </div>
    </>
  );
}
