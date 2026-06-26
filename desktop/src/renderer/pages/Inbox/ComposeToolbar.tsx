import "./ComposeToolbar.css";
import { useState } from "react";
import {
  IconBold,
  IconItalic,
  IconUnderline,
  IconPalette,
  IconHighlighter,
  IconAlignLeft,
  IconAlignCenter,
  IconAlignRight,
  IconAlignJustify,
  IconListUl,
  IconListOl,
  IconIndent,
  IconOutdent,
  IconUndo,
  IconRedo,
} from "../../components/ui/icons";

interface ComposeToolbarProps {
  execFormat: (command: string, value?: string) => void;
  resetTextColor: () => void;
  toggleHighlight: (color: string) => void;
  resetHighlight: () => void;
}

const FONT_OPTIONS = [
  { label: "Sans Serif", value: "Arial" },
  { label: "Serif", value: "Georgia" },
  { label: "Monospace", value: "Courier New" },
];

const SIZE_OPTIONS = [
  { label: "Petite", value: "2" },
  { label: "Normale", value: "3" },
  { label: "Grande", value: "5" },
  { label: "Très grande", value: "7" },
];

const TEXT_COLORS = [
  { label: "Noir", value: "#1a1a1a" },
  { label: "Rouge", value: "#e53935" },
  { label: "Bleu", value: "#1e88e5" },
  { label: "Vert", value: "#43a047" },
  { label: "Jaune", value: "#fbc02d" },
];

const HIGHLIGHT_COLORS = [
  { label: "Jaune", value: "#fff200" },
  { label: "Rose", value: "#ff4fa3" },
  { label: "Bleu", value: "#29b6f6" },
];

function preventBlur(e: React.MouseEvent) {
  e.preventDefault();
}

export default function ComposeToolbar({ execFormat, resetTextColor, toggleHighlight, resetHighlight }: ComposeToolbarProps) {
  const [colorMenuOpen, setColorMenuOpen] = useState(false);
  const [highlightMenuOpen, setHighlightMenuOpen] = useState(false);

  return (
    <div className="compose-toolbar">
      <select
        className="compose-toolbar__select"
        defaultValue={FONT_OPTIONS[0].value}
        onChange={(e) => execFormat("fontName", e.target.value)}
        title="Police"
      >
        {FONT_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      <select
        className="compose-toolbar__select"
        defaultValue={SIZE_OPTIONS[1].value}
        onChange={(e) => execFormat("fontSize", e.target.value)}
        title="Taille"
      >
        {SIZE_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      <span className="compose-toolbar__separator" />

      <button type="button" className="compose-toolbar__btn" onMouseDown={preventBlur} onClick={() => execFormat("bold")} title="Gras">
        <IconBold />
      </button>
      <button type="button" className="compose-toolbar__btn" onMouseDown={preventBlur} onClick={() => execFormat("italic")} title="Italique">
        <IconItalic />
      </button>
      <button
        type="button"
        className="compose-toolbar__btn"
        onMouseDown={preventBlur}
        onClick={() => execFormat("underline")}
        title="Souligné"
      >
        <IconUnderline />
      </button>
      <div className="compose-toolbar__color-wrap">
        <button
          type="button"
          className="compose-toolbar__btn"
          onMouseDown={preventBlur}
          onClick={() => setColorMenuOpen((o) => !o)}
          title="Couleur du texte"
        >
          <IconPalette />
        </button>
        {colorMenuOpen && (
          <>
            <div className="compose-toolbar__color-backdrop" onClick={() => setColorMenuOpen(false)} />
            <div className="compose-toolbar__color-menu">
              <button
                type="button"
                className="compose-toolbar__color-swatch compose-toolbar__color-swatch--default"
                title="Couleur par défaut"
                onMouseDown={preventBlur}
                onClick={() => {
                  resetTextColor();
                  setColorMenuOpen(false);
                }}
              />
              {TEXT_COLORS.map((color) => (
                <button
                  key={color.value}
                  type="button"
                  className="compose-toolbar__color-swatch"
                  style={{ backgroundColor: color.value }}
                  title={color.label}
                  onMouseDown={preventBlur}
                  onClick={() => {
                    execFormat("foreColor", color.value);
                    setColorMenuOpen(false);
                  }}
                />
              ))}
            </div>
          </>
        )}
      </div>

      <div className="compose-toolbar__color-wrap">
        <button
          type="button"
          className="compose-toolbar__btn"
          onMouseDown={preventBlur}
          onClick={() => setHighlightMenuOpen((o) => !o)}
          title="Surligner"
        >
          <IconHighlighter />
        </button>
        {highlightMenuOpen && (
          <>
            <div className="compose-toolbar__color-backdrop" onClick={() => setHighlightMenuOpen(false)} />
            <div className="compose-toolbar__color-menu">
              <button
                type="button"
                className="compose-toolbar__color-swatch compose-toolbar__color-swatch--default"
                title="Aucun surlignage"
                onMouseDown={preventBlur}
                onClick={() => {
                  resetHighlight();
                  setHighlightMenuOpen(false);
                }}
              />
              {HIGHLIGHT_COLORS.map((color) => (
                <button
                  key={color.value}
                  type="button"
                  className="compose-toolbar__color-swatch"
                  style={{ backgroundColor: color.value }}
                  title={color.label}
                  onMouseDown={preventBlur}
                  onClick={() => {
                    toggleHighlight(color.value);
                    setHighlightMenuOpen(false);
                  }}
                />
              ))}
            </div>
          </>
        )}
      </div>

      <span className="compose-toolbar__separator" />

      <button
        type="button"
        className="compose-toolbar__btn"
        onMouseDown={preventBlur}
        onClick={() => execFormat("justifyLeft")}
        title="Aligner à gauche"
      >
        <IconAlignLeft />
      </button>
      <button
        type="button"
        className="compose-toolbar__btn"
        onMouseDown={preventBlur}
        onClick={() => execFormat("justifyCenter")}
        title="Centrer"
      >
        <IconAlignCenter />
      </button>
      <button
        type="button"
        className="compose-toolbar__btn"
        onMouseDown={preventBlur}
        onClick={() => execFormat("justifyRight")}
        title="Aligner à droite"
      >
        <IconAlignRight />
      </button>
      <button
        type="button"
        className="compose-toolbar__btn"
        onMouseDown={preventBlur}
        onClick={() => execFormat("justifyFull")}
        title="Justifier"
      >
        <IconAlignJustify />
      </button>

      <span className="compose-toolbar__separator" />

      <button
        type="button"
        className="compose-toolbar__btn"
        onMouseDown={preventBlur}
        onClick={() => execFormat("insertUnorderedList")}
        title="Liste à puces"
      >
        <IconListUl />
      </button>
      <button
        type="button"
        className="compose-toolbar__btn"
        onMouseDown={preventBlur}
        onClick={() => execFormat("insertOrderedList")}
        title="Liste numérotée"
      >
        <IconListOl />
      </button>
      <button type="button" className="compose-toolbar__btn" onMouseDown={preventBlur} onClick={() => execFormat("indent")} title="Augmenter le retrait">
        <IconIndent />
      </button>
      <button type="button" className="compose-toolbar__btn" onMouseDown={preventBlur} onClick={() => execFormat("outdent")} title="Diminuer le retrait">
        <IconOutdent />
      </button>

      <span className="compose-toolbar__separator" />

      <button type="button" className="compose-toolbar__btn" onMouseDown={preventBlur} onClick={() => execFormat("undo")} title="Annuler">
        <IconUndo />
      </button>
      <button type="button" className="compose-toolbar__btn" onMouseDown={preventBlur} onClick={() => execFormat("redo")} title="Rétablir">
        <IconRedo />
      </button>
    </div>
  );
}
