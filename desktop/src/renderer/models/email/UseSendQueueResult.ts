import type { PendingSend } from "./PendingSend";

export interface UseSendQueueResult {
  pendingSend: PendingSend | null;
  requestSend: (draftId: string, subject: string) => void;
  cancelSend: () => void;
}
