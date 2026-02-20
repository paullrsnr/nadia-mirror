import { useState, useEffect, useCallback } from "react";
import type { LLMStatusResponse, InstalledModel, CatalogModel } from "../models/llm";
import {
  getLLMStatus,
  getCatalog,
  downloadModelWithProgress,
  loadModel,
} from "../services/apis/llm.api";
import { colors, spacing, radius } from "../theme";

export default function IA() {
  const [status, setStatus] = useState<LLMStatusResponse | null>(null);
  const [installedModels, setInstalledModels] = useState<InstalledModel[]>([]);
  const [catalog, setCatalog] = useState<CatalogModel[]>([]);
  const [modelLoading, setModelLoading] = useState(false);
  /** Téléchargements en cours : { [modelId]: { modelName, percent } } */
  const [downloadProgress, setDownloadProgress] = useState<Record<string, { modelName: string; percent: number }>>({});
  const [error, setError] = useState<string | null>(null);
  /** Catégories déroulées dans l'accordéon */
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  const refresh = useCallback(() => {
    getLLMStatus()
      .then((s) => {
        setStatus(s);
        setInstalledModels(s?.installed_models ?? []);
      })
      .catch(() => {
        setStatus({ available: false, message: "Impossible de joindre l'API" });
        setInstalledModels([]);
      });
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    getCatalog()
      .then((r) => setCatalog(r.models))
      .catch(() => setCatalog([]));
  }, []);

  async function handleSelectModel(modelId: string) {
    if (status?.selected_model_id === modelId) return;
    setError(null);
    setModelLoading(true);
    try {
      await loadModel(modelId);
      refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur chargement modèle");
    } finally {
      setModelLoading(false);
    }
  }

  function isInstalled(entry: CatalogModel): boolean {
    return installedModels.some((m) => m.id === entry.filename || m.id === entry.id);
  }

  function toggleCategory(category: string) {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  }

  // Grouper les modèles par catégorie
  const modelsByCategory = catalog.reduce((acc, model) => {
    const cat = model.category || "Autre";
    if (!acc[cat]) {
      acc[cat] = [];
    }
    acc[cat].push(model);
    return acc;
  }, {} as Record<string, CatalogModel[]>);

  // Ordre des catégories pour l'affichage
  const categoryOrder = ["Très léger", "Léger", "Moyen", "Haute qualité", "Très haute qualité", "Autre"];
  const sortedCategories = categoryOrder.filter((cat) => modelsByCategory[cat]?.length > 0);

  async function handleDownload(entry: CatalogModel) {
    setError(null);
    // Démarrer le téléchargement
    setDownloadProgress((prev) => ({
      ...prev,
      [entry.id]: { modelName: entry.name, percent: 0 },
    }));
    try {
      await downloadModelWithProgress(entry.repo, entry.filename, {
        onProgress: (p) =>
          setDownloadProgress((prev) => ({
            ...prev,
            [entry.id]: { modelName: entry.name, percent: p.percent },
          })),
      });
      refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur téléchargement");
    } finally {
      // Retirer ce téléchargement de la liste
      setDownloadProgress((prev) => {
        const next = { ...prev };
        delete next[entry.id];
        return next;
      });
    }
  }

  const currentId = status?.selected_model_id ?? (installedModels.length ? installedModels[0].id : null);

  const activeDownloads = Object.entries(downloadProgress);
  const isSingleDownload = activeDownloads.length === 1;
  const singleDownload = isSingleDownload ? activeDownloads[0] : null;
  const hasNoInstalledModels = installedModels.length === 0;

  // Écran plein pour un seul téléchargement si aucun modèle n'est déjà installé
  if (isSingleDownload && singleDownload && hasNoInstalledModels) {
    const progress = singleDownload[1];
    return (
      <div
        style={{
          position: "fixed",
          inset: 0,
          background: colors.buttonSecondary ?? "#fff",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
          padding: spacing.page,
        }}
      >
        {/* Animation de chargement */}
        <div
          style={{
            width: 60,
            height: 60,
            border: `4px solid ${colors.border ?? "#e0e0e0"}`,
            borderTopColor: colors.buttonPrimary ?? "#1976d2",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
            marginBottom: spacing.md,
          }}
        />
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>

        <h3 style={{ fontSize: "18px", color: colors.textPrimary, marginBottom: spacing.sm, textAlign: "center" }}>
          Téléchargement en cours
        </h3>
        <p style={{ fontSize: "14px", color: colors.textSecondary, marginBottom: spacing.md, textAlign: "center" }}>
          {progress.modelName}
        </p>

        {/* Barre de progression */}
        <div style={{ width: "100%", maxWidth: 400 }}>
          <div
            style={{
              height: 8,
              background: colors.border ?? "#e0e0e0",
              borderRadius: 4,
              overflow: "hidden",
              marginBottom: spacing.xs,
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${Math.min(100, Math.max(0, progress.percent))}%`,
                background: colors.buttonPrimary ?? "#1976d2",
                borderRadius: 4,
                transition: "width 0.2s ease",
              }}
            />
          </div>
          <p style={{ fontSize: "16px", color: colors.textPrimary, textAlign: "center", fontWeight: 500 }}>
            {progress.percent.toFixed(1)}%
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: spacing.page, maxWidth: 600 }}>
      <h2 style={{ margin: `0 0 ${spacing.page}px`, color: colors.textPrimary, fontSize: "18px" }}>
        IA locale
      </h2>

      {/* Barres de progression des téléchargements en cours (plusieurs) */}
      {activeDownloads.length > 0 && (
        <div
          style={{
            marginBottom: spacing.md,
            padding: spacing.sm,
            background: colors.backgroundMuted,
            borderRadius: radius.md,
            border: `1px solid ${colors.border}`,
          }}
        >
          <p style={{ margin: `0 0 ${spacing.xs}px`, fontSize: "12px", color: colors.textSecondary, fontWeight: 500 }}>
            Téléchargements en cours
          </p>
          {activeDownloads.map(([modelId, progress]) => (
            <div key={modelId} style={{ marginTop: spacing.xs }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <span style={{ fontSize: "12px", color: colors.textPrimary }}>{progress.modelName}</span>
                <span style={{ fontSize: "11px", color: colors.textSecondary }}>
                  {progress.percent.toFixed(1)}%
                </span>
              </div>
              <div
                style={{
                  height: 6,
                  background: colors.border ?? "#e0e0e0",
                  borderRadius: 3,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${Math.min(100, Math.max(0, progress.percent))}%`,
                    background: colors.buttonPrimary ?? "#1976d2",
                    borderRadius: 3,
                    transition: "width 0.2s ease",
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {status && (
        <p
          style={{
            marginBottom: spacing.sm,
            padding: spacing.md,
            borderRadius: radius.md,
            background: status.available ? "#e8f5e9" : "#ffebee",
            color: status.available ? colors.success : colors.error,
            fontSize: "13px",
          }}
        >
          {status.available ? "✓ " : "✗ "}
          {status.message}
        </p>
      )}

      {installedModels.length === 0 && catalog.length > 0 && (
        <p
          style={{
            marginBottom: spacing.md,
            padding: spacing.sm,
            fontSize: "13px",
            color: colors.textSecondary,
          }}
        >
          Aucun modèle installé. Téléchargez-en un ci-dessous (plusieurs Go, première fois uniquement).
        </p>
      )}

      {catalog.length > 0 && (
        <div style={{ marginBottom: spacing.page }}>
          <h3 style={{ fontSize: "14px", margin: `0 0 ${spacing.sm}px`, color: colors.textPrimary }}>
            Télécharger un modèle
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: spacing.xs }}>
            {sortedCategories.map((category) => {
              const models = modelsByCategory[category];
              const isExpanded = expandedCategories.has(category);
              return (
                <div
                  key={category}
                  style={{
                    border: `1px solid ${colors.border}`,
                    borderRadius: radius.md,
                    overflow: "hidden",
                  }}
                >
                  <button
                    type="button"
                    onClick={() => toggleCategory(category)}
                    style={{
                      width: "100%",
                      padding: spacing.sm,
                      background: colors.backgroundMuted,
                      border: "none",
                      textAlign: "left",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      fontSize: "13px",
                      fontWeight: 500,
                      color: colors.textPrimary,
                    }}
                  >
                    <span>
                      {category} <span style={{ color: colors.textSecondary, fontWeight: 400 }}>({models.length})</span>
                    </span>
                    <span
                      style={{
                        fontSize: "16px",
                        transition: "transform 0.2s",
                        transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)",
                      }}
                    >
                      ▶
                    </span>
                  </button>
                  {isExpanded && (
                    <ul style={{ listStyle: "none", padding: spacing.xs, margin: 0, background: colors.buttonSecondary }}>
                      {models.map((entry) => {
                        const installed = isInstalled(entry);
                        const downloading = entry.id in downloadProgress;
                        let buttonLabel: string;
                        if (installed) buttonLabel = "Installé";
                        else if (downloading) buttonLabel = "Téléchargement…";
                        else buttonLabel = "Télécharger";
                        return (
                          <li
                            key={entry.id}
                            style={{
                              display: "flex",
                              alignItems: "flex-start",
                              gap: spacing.sm,
                              padding: spacing.sm,
                              marginBottom: spacing.xs,
                              background: colors.backgroundMuted,
                              borderRadius: radius.sm,
                            }}
                          >
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <strong style={{ fontSize: "13px", color: colors.textPrimary }}>{entry.name}</strong>
                              {entry.description && (
                                <p style={{ margin: "2px 0 0", fontSize: "12px", color: colors.textSecondary }}>
                                  {entry.description}
                                </p>
                              )}
                            </div>
                            <button
                              type="button"
                              disabled={installed || downloading}
                              onClick={() => handleDownload(entry)}
                              style={{
                                padding: `${spacing.xs}px ${spacing.sm}px`,
                                fontSize: "12px",
                                background: installed ? colors.backgroundMuted : colors.buttonPrimary,
                                color: installed ? colors.textMuted : colors.buttonSecondary,
                                border: "none",
                                borderRadius: radius.sm,
                                cursor: installed || downloading ? "not-allowed" : "pointer",
                                opacity: downloading ? 0.8 : 1,
                                flexShrink: 0,
                              }}
                            >
                              {buttonLabel}
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {installedModels.length > 0 && (
        <div style={{ marginBottom: spacing.page }}>
          <label
            htmlFor="ia-model"
            style={{ display: "block", marginBottom: spacing.xs, fontSize: "12px", color: colors.textSecondary }}
          >
            Modèle utilisé
          </label>
          <select
            id="ia-model"
            value={currentId ?? ""}
            onChange={(e) => handleSelectModel(e.target.value)}
            disabled={modelLoading}
            style={{
              width: "100%",
              padding: spacing.sm,
              border: `1px solid ${colors.border}`,
              borderRadius: radius.sm,
              fontSize: "14px",
              background: colors.buttonSecondary,
              cursor: modelLoading ? "not-allowed" : "pointer",
              boxSizing: "border-box",
            }}
          >
            {installedModels.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
          {modelLoading && (
            <span style={{ fontSize: "12px", color: colors.textMuted, marginLeft: spacing.xs }}>
              Chargement…
            </span>
          )}
        </div>
      )}

      {error && (
        <p style={{ color: colors.error, fontSize: "13px", marginBottom: spacing.md }}>{error}</p>
      )}
    </div>
  );
}
