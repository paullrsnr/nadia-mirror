import type { Category, CategoryChipColors, CategoryChipOverrides } from "../../models/email";

export const colors = {
  /* Surfaces */
  base:       "var(--color-base)",
  baseSoft:   "var(--color-base-soft)",
  baseMuted:  "var(--color-base-muted)",
  baseStrong: "var(--color-base-strong)",
  selected:   "var(--color-selected)",
  unread:     "var(--color-unread)",
  hover:      "var(--color-hover)",

  /* Bordures */
  border:       "var(--color-border)",
  borderSoft:   "var(--color-border-soft)",
  borderStrong: "var(--color-border-strong)",

  /* Texte */
  content:         "var(--color-content)",
  contentSoft:     "var(--color-content-soft)",
  contentMuted:    "var(--color-content-muted)",
  contentInverted: "var(--color-content-inverted)",

  /* Marque */
  marquePrimary:              "var(--color-marque-primary)",
  marquePrimaryHover:         "var(--color-marque-primary-hover)",
  marqueSecondary:            "var(--color-marque-secondary)",
  marqueSecondaryHover:       "var(--color-marque-secondary-hover)",
  marqueTertiary:             "var(--color-marque-tertiary)",
  marquePrimarySurfaceBorder: "var(--color-marque-primary-surface-border)",
  marqueSecondarySurface:     "var(--color-marque-secondary-surface)",

  /* Badges & chips */
  badgeBg:           "var(--color-badge-bg)",
  badgeTxt:          "var(--color-badge-txt)",
  starActive:        "var(--color-star-active)",
  starInactive:      "var(--color-star-inactive)",
  starHover:         "var(--color-star-hover)",
  chipUrgentBg:      "var(--color-chip-urgent-bg)",
  chipUrgentTxt:     "var(--color-chip-urgent-txt)",
  chipImportantBg:   "var(--color-chip-important-bg)",
  chipImportantTxt:  "var(--color-chip-important-txt)",
  chipPromoBg:       "var(--color-chip-promo-bg)",
  chipPromoTxt:      "var(--color-chip-promo-txt)",

  /* Statuts (app/success, app/info, app/warning, app/error — Figma) */
  success:        "var(--color-success)",
  successHover:   "var(--color-success-hover)",
  successBorder:  "var(--color-success-border)",
  successContent: "var(--color-success-content)",
  info:           "var(--color-info)",
  infoHover:      "var(--color-info-hover)",
  infoBorder:     "var(--color-info-border)",
  infoContent:    "var(--color-info-content)",
  warning:        "var(--color-warning)",
  warningHover:   "var(--color-warning-hover)",
  warningBorder:  "var(--color-warning-border)",
  warningContent: "var(--color-warning-content)",
  error:          "var(--color-error)",
  errorHover:     "var(--color-error-hover)",
  errorBorder:    "var(--color-error-border)",
  errorContent:   "var(--color-error-content)",
} as const;

export const DEFAULT_CATEGORY_CHIP_COLORS: Record<Category["name"], CategoryChipColors> = {
  finance:      { bg: "var(--color-chip-important-bg)", txt: "var(--color-chip-important-txt)" },
  shopping:     { bg: "var(--color-chip-promo-bg)", txt: "var(--color-chip-promo-txt)" },
  marketing:    { bg: "var(--color-chip-urgent-bg)", txt: "var(--color-chip-urgent-txt)" },
  travail:      { bg: "var(--color-marque-secondary-surface)", txt: "var(--color-marque-secondary)" },
  personnel:    { bg: "var(--color-marque-primary-surface-border)", txt: "var(--color-marque-primary)" },
  notification: { bg: "var(--color-base-muted)", txt: "var(--color-content-muted)" },
  autre:        { bg: "var(--color-base-muted)", txt: "var(--color-content-muted)" },
};

export function getCategoryChipColor(
  category: Category["name"],
  userOverrides?: CategoryChipOverrides,
): CategoryChipColors {
  return userOverrides?.[category] ?? DEFAULT_CATEGORY_CHIP_COLORS[category];
}
