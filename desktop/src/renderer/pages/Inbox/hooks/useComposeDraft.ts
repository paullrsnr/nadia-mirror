import { useEffect, useRef, useState } from "react";
import { deleteAttachment, saveDraft, uploadAttachment } from "../../../services/api/drafts.api";
import { DEFAULT_TEXT_COLOR } from "../../../constants/compose";
import type {
  ComposeMode,
  DraftEmail,
  Email,
  EmailAddress,
  EmailAttachment,
  UseComposeDraftOptions,
  UseComposeDraftResult,
} from "../../../models";

function joinAddresses(addresses: EmailAddress[]): string {
  return addresses.map((a) => a.email).join(", ");
}

const AUTOSAVE_DELAY_MS = 800;

function initialSubject(mode: ComposeMode, replyTo?: Email): string {
  if (!replyTo) return "";
  if (mode === "reply") return `Re: ${replyTo.subject}`;
  if (mode === "forward") return `Fwd: ${replyTo.subject}`;
  return "";
}

function initialBodyText(mode: ComposeMode, replyTo?: Email): string {
  if (mode === "forward" && replyTo) {
    return `\n\n---------- Message transféré ----------\n${replyTo.body_text}`;
  }
  return "";
}

function escapeHtml(text: string): string {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function textToHtml(text: string): string {
  return escapeHtml(text).replace(/\n/g, "<br>");
}

function hexToRgb(hex: string): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgb(${r}, ${g}, ${b})`;
}

function htmlToPlainText(html: string): string {
  const container = document.createElement("div");
  container.innerHTML = html;
  return container.innerText ?? container.textContent ?? "";
}

function initialHtml(mode: ComposeMode, replyTo?: Email, existingDraft?: DraftEmail): string {
  if (existingDraft) {
    return existingDraft.body_html ?? textToHtml(existingDraft.body_text);
  }
  return textToHtml(initialBodyText(mode, replyTo));
}

export function useComposeDraft({
  provider,
  mode,
  replyTo,
  existingDraft,
  onSent,
}: UseComposeDraftOptions): UseComposeDraftResult {
  const draftId = useRef(existingDraft?.id ?? crypto.randomUUID());
  const touched = useRef(false);
  const bodyRef = useRef<HTMLDivElement>(null);
  const savedRange = useRef<Range | null>(null);
  const initialBodyHtml = useRef(initialHtml(mode, replyTo, existingDraft)).current;

  useEffect(() => {
    function handleSelectionChange() {
      const selection = document.getSelection();
      if (!selection || selection.rangeCount === 0) return;
      const range = selection.getRangeAt(0);
      if (bodyRef.current?.contains(range.commonAncestorContainer)) {
        savedRange.current = range.cloneRange();
      }
    }
    document.addEventListener("selectionchange", handleSelectionChange);
    return () => document.removeEventListener("selectionchange", handleSelectionChange);
  }, []);

  const [to, setTo] = useState(
    existingDraft ? joinAddresses(existingDraft.to_addresses)
      : mode === "reply" && replyTo ? replyTo.from_address.email : "",
  );
  const [cc, setCc] = useState(existingDraft ? joinAddresses(existingDraft.cc_addresses) : "");
  const [bcc, setBcc] = useState(existingDraft ? joinAddresses(existingDraft.bcc_addresses) : "");
  const [ccVisible, setCcVisible] = useState(Boolean(existingDraft && existingDraft.cc_addresses.length > 0));
  const [bccVisible, setBccVisible] = useState(Boolean(existingDraft && existingDraft.bcc_addresses.length > 0));
  const [subject, setSubject] = useState(existingDraft ? existingDraft.subject : initialSubject(mode, replyTo));
  const [body, setBody] = useState(initialBodyHtml);
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<EmailAttachment[]>(existingDraft?.attachments ?? []);
  const [uploadingAttachment, setUploadingAttachment] = useState(false);

  const buildPayload = () => ({
    provider,
    to: splitAddresses(to),
    cc: splitAddresses(cc),
    bcc: splitAddresses(bcc),
    subject,
    body_text: htmlToPlainText(body),
    body_html: body,
    in_reply_to_email_id: existingDraft?.in_reply_to_email_id ?? (mode === "reply" ? replyTo?.id : undefined),
  });

  useEffect(() => {
    if (!touched.current) {
      touched.current = to !== "" || cc !== "" || bcc !== "" || subject !== "" || body !== initialBodyHtml;
      if (!touched.current) return;
    }
    setSaving(true);
    const timer = setTimeout(() => {
      saveDraft(draftId.current, buildPayload())
        .catch(() => {})
        .finally(() => setSaving(false));
    }, AUTOSAVE_DELAY_MS);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [to, cc, bcc, subject, body]);

  function handleBodyInput() {
    setBody(bodyRef.current?.innerHTML ?? "");
  }

  function execFormat(command: string, value?: string) {
    restoreSelection();
    document.execCommand(command, false, value);
    handleBodyInput();
  }

  function restoreSelection() {
    bodyRef.current?.focus();
    const selection = document.getSelection();
    if (selection && savedRange.current) {
      selection.removeAllRanges();
      selection.addRange(savedRange.current);
    }
  }

  function applyDefaultTextColor() {
    const defaultColor = bodyRef.current ? getComputedStyle(bodyRef.current).color : "";
    if (defaultColor) document.execCommand("foreColor", false, defaultColor);
  }

  function resetTextColor() {
    restoreSelection();
    applyDefaultTextColor();
    handleBodyInput();
  }

  function toggleHighlight(color: string) {
    restoreSelection();
    const isActive = document.queryCommandValue("backColor") === hexToRgb(color);
    document.execCommand("backColor", false, isActive ? "transparent" : color);
    if (isActive) applyDefaultTextColor();
    else document.execCommand("foreColor", false, DEFAULT_TEXT_COLOR);
    handleBodyInput();
  }

  function resetHighlight() {
    restoreSelection();
    document.execCommand("backColor", false, "transparent");
    applyDefaultTextColor();
    handleBodyInput();
  }

  function showCc() {
    setCcVisible(true);
  }

  function showBcc() {
    setBccVisible(true);
  }

  async function handleAddAttachments(files: FileList) {
    setUploadingAttachment(true);
    try {
      for (const file of Array.from(files)) {
        const attachment = await uploadAttachment(draftId.current, file);
        setAttachments((prev) => [...prev, attachment]);
      }
    } catch {
      setSendError("Erreur lors de l'ajout de la pièce jointe.");
    } finally {
      setUploadingAttachment(false);
    }
  }

  async function handleRemoveAttachment(attachmentId: string) {
    await deleteAttachment(draftId.current, attachmentId).catch(() => {});
    setAttachments((prev) => prev.filter((a) => a.attachment_id !== attachmentId));
  }

  async function handleSend() {
    setSending(true);
    setSendError(null);
    try {
      await saveDraft(draftId.current, buildPayload());
      onSent(draftId.current, subject);
    } catch {
      setSendError("Erreur lors de l'envoi de l'email.");
    } finally {
      setSending(false);
    }
  }

  return {
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
  };
}

function splitAddresses(value: string): string[] {
  return value
    .split(",")
    .map((a) => a.trim())
    .filter(Boolean);
}
