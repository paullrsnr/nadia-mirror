import "./Toolbar.css";
import { useEffect, useState } from "react";
import { useComputed } from "@preact/signals-react";
import { getLlmStatus, loadModel } from "../../../services/api/llm.api";
import { llmStatusSignal } from "../../../state";
import { IconSearch, IconChevronDown } from "../../ui/icons";
import ComposeActionButton from "../ComposeActionButton";
import type { ToolbarProps } from "../../../models/layout";
import { THEME_ICON, THEME_LABEL } from "../../../constants/theme";

export default function Toolbar({ searchValue, onSearchChange, themePreference, onCycleTheme, onComposeClick }: ToolbarProps) {
  const status = useComputed(() => llmStatusSignal.value).value;
  const [switching, setSwitching] = useState(false);
  const [modelError, setModelError] = useState<string | null>(null);

  useEffect(() => {
    if (!status) getLlmStatus().then((s) => (llmStatusSignal.value = s)).catch(() => {});
  }, [status]);

  const installedModels = status?.installed_models ?? [];
  const ThemeIcon = THEME_ICON[themePreference];

  async function handleModelChange(modelId: string) {
    if (!modelId || modelId === status?.selected_model_id) return;
    setSwitching(true);
    setModelError(null);
    try {
      await loadModel(modelId);
      llmStatusSignal.value = await getLlmStatus();
    } catch {
      setModelError("Erreur lors du chargement du modèle");
    } finally {
      setSwitching(false);
    }
  }

  return (
    <header className="toolbar">
      <div className="toolbar__search">
        <IconSearch className="toolbar__search-icon" />
        <input
          type="text"
          className="toolbar__search-input"
          placeholder="Rechercher dans tous les emails..."
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      <ComposeActionButton mode="new" onClick={onComposeClick} className="toolbar__compose" />

      <div className="toolbar__right">
        <button
          type="button"
          className="toolbar__icon-btn"
          onClick={onCycleTheme}
          title={`Thème : ${THEME_LABEL[themePreference]}`}
          aria-label={`Changer de thème (actuel : ${THEME_LABEL[themePreference]})`}
        >
          <ThemeIcon />
        </button>

        <div className="toolbar__model">
          <span className="toolbar__model-label">Modèle IA :</span>
          <div className="toolbar__model-select-wrap">
            <select
              className="toolbar__model-select"
              value={status?.selected_model_id ?? ""}
              onChange={(e) => handleModelChange(e.target.value)}
              disabled={installedModels.length === 0 || switching}
              title={modelError ?? undefined}
            >
              {installedModels.length === 0 && <option value="">Aucun modèle</option>}
              {!status?.selected_model_id && <option value="">Sélectionner...</option>}
              {installedModels.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
            <IconChevronDown className="toolbar__model-chevron" />
          </div>
          {switching && <span className="toolbar__model-status">Chargement...</span>}
          {!switching && modelError && (
            <span className="toolbar__model-status toolbar__model-status--error">{modelError}</span>
          )}
        </div>
      </div>
    </header>
  );
}
