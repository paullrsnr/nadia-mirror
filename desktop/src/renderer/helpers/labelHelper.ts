import { UNREAD_LABEL } from "../constants/labels";

export function applyReadLabel(labels: string[], read: boolean): string[] {
  const next = new Set(labels);
  if (read) next.delete(UNREAD_LABEL);
  else next.add(UNREAD_LABEL);
  return [...next];
}
