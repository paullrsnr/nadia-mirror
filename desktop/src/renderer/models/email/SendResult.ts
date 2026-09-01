import type { ConnectableProvider } from "../auth/ConnectableProvider";

export interface SendResult {
  status: "success" | "error";
  draft_id: string;
  provider?: ConnectableProvider | null;
}
