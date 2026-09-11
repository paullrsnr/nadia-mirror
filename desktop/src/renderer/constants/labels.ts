import type { ComposeActionMode, ComposeMode, InboxFolder } from "../models";

export const UNREAD_LABEL = "UNREAD";
export const COMING_SOON_LABEL = "Bientôt disponible";

export function getStarTitle(starred: boolean): string {
  return starred ? "Retirer des favoris" : "Ajouter aux favoris";
}

export const FOLDER_TITLES: Record<InboxFolder, string> = {
  inbox: "Boîte de réception",
  favoris: "Favoris",
  sent: "Envoyés",
  drafts: "Brouillons",
};

export const COMPOSE_MODE_TITLES: Record<ComposeMode, string> = {
  new: "Nouveau message",
  reply: "Répondre",
  forward: "Transférer",
  draft: "Brouillon",
};

export const COMPOSE_ACTION_LABELS: Record<ComposeActionMode, string> = {
  new: "Nouveau message",
  send: "Envoyer",
};
