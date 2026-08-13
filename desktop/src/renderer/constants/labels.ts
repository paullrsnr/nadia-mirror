export const UNREAD_LABEL = "UNREAD";
export const COMING_SOON_LABEL = "Bientôt disponible";

export function getStarTitle(starred: boolean): string {
  return starred ? "Retirer des favoris" : "Ajouter aux favoris";
}
