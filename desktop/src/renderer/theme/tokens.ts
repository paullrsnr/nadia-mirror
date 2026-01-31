/**
 * Design tokens partagés : couleurs, espacements, typo, rayons.
 * Rôle sémantique pour chaque valeur — changer ici pour appliquer l’identité.
 */

// —— Couleurs (rôles sémantiques)
export const colors = {
  /** Fond principal (pages, cartes) */
  background: "#ffffff",
  /** Fond secondaire (header, zones atténuées) */
  backgroundMuted: "#f9f9f9",
  /** Fond carte email non lue */
  backgroundUnread: "#f0f7ff",
  /** Fond survol (hover) */
  backgroundHover: "#f5f5f5",
  /** Fond overlay / page modale (auth callback, etc.) */
  backgroundOverlay: "#f5f5f5",

  /** Bordure légère (séparateurs, champs) */
  border: "#eee",
  /** Bordure plus marquée (panneaux, boutons secondaires) */
  borderStrong: "#ddd",
  /** Bordure bouton secondaire */
  borderButton: "#ccc",

  /** Texte principal */
  textPrimary: "#333333",
  /** Texte secondaire (sujet, métadonnées) */
  textSecondary: "#666666",
  /** Texte atténué (snippet, date, placeholder) */
  textMuted: "#888888",

  /** Succès (validation, auth OK) */
  success: "#4CAF50",
  /** Erreur (alertes, auth KO) */
  error: "#f44336",

  /** Bouton primaire (CTA) */
  buttonPrimary: "#007bff",
  /** Fond bouton secondaire */
  buttonSecondary: "#ffffff",
} as const;

// —— Espacements (px)
export const spacing = {
  xs: 5,
  sm: 8,
  md: 10,
  card: 15,
  page: 20,
  lg: 40,
} as const;

// —— Typographie
export const typography = {
  fontFamily: "Arial, sans-serif",
  fontSizeXs: "11px",
  fontSizeSm: "12px",
  fontSizeBase: "14px",
  fontWeightNormal: "normal",
  fontWeightBold: "bold",
} as const;

// —— Rayons (border-radius, px)
export const radius = {
  sm: 3,
  md: 8,
} as const;

// —— Ombres
export const shadow = {
  card: "0 2px 10px rgba(0,0,0,0.1)",
} as const;
