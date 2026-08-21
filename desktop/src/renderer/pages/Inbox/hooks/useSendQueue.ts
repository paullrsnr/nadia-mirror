import { useCallback, useEffect, useRef, useState } from "react";
import { sendDraft } from "../../../services/api/drafts.api";
import type { PendingSend, UseSendQueueOptions, UseSendQueueResult } from "../../../models";

const SEND_DELAY_MS = 2000;

export function useSendQueue({ onSendComplete }: UseSendQueueOptions): UseSendQueueResult {
  const [pendingSend, setPendingSend] = useState<PendingSend | null>(null);
  const timeoutRef = useRef<number | null>(null);
  const onSendCompleteRef = useRef(onSendComplete);

  useEffect(() => {
    onSendCompleteRef.current = onSendComplete;
  }, [onSendComplete]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current);
    };
  }, []);

  const requestSend = useCallback((draftId: string, subject: string) => {
    timeoutRef.current = window.setTimeout(() => {
      timeoutRef.current = null;
      setPendingSend(null);
      sendDraft(draftId).finally(() => onSendCompleteRef.current());
    }, SEND_DELAY_MS);
    setPendingSend({ draftId, subject });
  }, []);

  const cancelSend = useCallback(() => {
    if (timeoutRef.current === null) return;
    window.clearTimeout(timeoutRef.current);
    timeoutRef.current = null;
    setPendingSend(null);
  }, []);

  return { pendingSend, requestSend, cancelSend };
}
