import { colors, spacing, radius, shadow } from "../../theme";
import type { CatalogModel, InstalledModel } from "../../types";
import Button from "../ui/Button";

interface ModelCardProps {
  model: CatalogModel;
  installed: InstalledModel | null;
  isSelected: boolean;
  isDownloading: boolean;
  downloadProgress: string | null;
  onDownload: () => void;
  onLoad: () => void;
}

export default function ModelCard({
  model,
  installed,
  isSelected,
  isDownloading,
  downloadProgress,
  onDownload,
  onLoad,
}: ModelCardProps) {
  const isInstalled = installed !== null;

  return (
    <div
      style={{
        padding: spacing.card,
        marginBottom: spacing.md,
        border: `1px solid ${isSelected ? colors.success : colors.border}`,
        borderRadius: radius.md,
        backgroundColor: isSelected ? "#f0fff0" : colors.background,
        boxShadow: shadow.card,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ margin: 0, marginBottom: spacing.xs, color: colors.textPrimary }}>
            {model.name}
            {isSelected && (
              <span style={{ marginLeft: spacing.sm, fontSize: "12px", color: colors.success, fontWeight: "normal" }}>
                ● Actif
              </span>
            )}
          </h3>
          <p style={{ margin: 0, marginBottom: spacing.sm, color: colors.textSecondary, fontSize: "13px" }}>
            {model.description}
          </p>
          <p style={{ margin: 0, color: colors.textMuted, fontSize: "11px" }}>
            {model.repo} / {model.filename}
          </p>
        </div>

        <div style={{ display: "flex", gap: spacing.sm, marginLeft: spacing.md, alignItems: "center" }}>
          {!isInstalled && !isDownloading && (
            <Button variant="primary" size="sm" onClick={onDownload}>
              Télécharger
            </Button>
          )}

          {isDownloading && (
            <span style={{ color: colors.textMuted, fontSize: "13px" }}>
              {downloadProgress || "Téléchargement..."}
            </span>
          )}

          {isInstalled && !isSelected && (
            <Button
              size="sm"
              onClick={onLoad}
              style={{ backgroundColor: colors.success, color: "white", border: "none" }}
            >
              Charger
            </Button>
          )}

          {isInstalled && (
            <span
              style={{
                padding: `${spacing.sm}px ${spacing.card}px`,
                backgroundColor: colors.backgroundMuted,
                color: colors.textSecondary,
                borderRadius: radius.sm,
                fontSize: "12px",
              }}
            >
              Installé
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
