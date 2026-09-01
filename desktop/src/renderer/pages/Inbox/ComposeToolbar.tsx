import "./ComposeToolbar.css";
import { Fragment } from "react";
import { preventBlur } from "../../helpers";
import ColorMenu from "./ColorMenu";
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
import type { ComposeFormatAction, ComposeToolbarProps, LabeledOption } from "../../models";

const FONT_OPTIONS: LabeledOption[] = [
  { label: "Sans Serif", value: "Arial" },
  { label: "Serif", value: "Georgia" },
  { label: "Monospace", value: "Courier New" },
];

const SIZE_OPTIONS: LabeledOption[] = [
  { label: "Petite", value: "2" },
  { label: "Normale", value: "3" },
  { label: "Grande", value: "5" },
  { label: "Très grande", value: "7" },
];

const TEXT_COLORS: LabeledOption[] = [
  { label: "Noir", value: "#1a1a1a" },
  { label: "Rouge", value: "#e53935" },
  { label: "Bleu", value: "#1e88e5" },
  { label: "Vert", value: "#43a047" },
  { label: "Jaune", value: "#fbc02d" },
];

const HIGHLIGHT_COLORS: LabeledOption[] = [
  { label: "Jaune", value: "#fff200" },
  { label: "Rose", value: "#ff4fa3" },
  { label: "Bleu", value: "#29b6f6" },
];

const FORMAT_GROUPS: ComposeFormatAction[][] = [
  [
    { command: "bold", title: "Gras", icon: IconBold },
    { command: "italic", title: "Italique", icon: IconItalic },
    { command: "underline", title: "Souligné", icon: IconUnderline },
  ],
  [
    { command: "justifyLeft", title: "Aligner à gauche", icon: IconAlignLeft },
    { command: "justifyCenter", title: "Centrer", icon: IconAlignCenter },
    { command: "justifyRight", title: "Aligner à droite", icon: IconAlignRight },
    { command: "justifyFull", title: "Justifier", icon: IconAlignJustify },
  ],
  [
    { command: "insertUnorderedList", title: "Liste à puces", icon: IconListUl },
    { command: "insertOrderedList", title: "Liste numérotée", icon: IconListOl },
    { command: "indent", title: "Augmenter le retrait", icon: IconIndent },
    { command: "outdent", title: "Diminuer le retrait", icon: IconOutdent },
  ],
  [
    { command: "undo", title: "Annuler", icon: IconUndo },
    { command: "redo", title: "Rétablir", icon: IconRedo },
  ],
];

export default function ComposeToolbar({ execFormat, resetTextColor, toggleHighlight, resetHighlight }: ComposeToolbarProps) {
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

      {FORMAT_GROUPS.map((group, index) => (
        <Fragment key={group[0].command}>
          <span className="compose-toolbar__separator" />
          {group.map(({ command, title, icon: Icon }) => (
            <button
              key={command}
              type="button"
              className="compose-toolbar__btn"
              onMouseDown={preventBlur}
              onClick={() => execFormat(command)}
              title={title}
            >
              <Icon />
            </button>
          ))}
          {index === 0 && (
            <>
              <ColorMenu
                title="Couleur du texte"
                icon={IconPalette}
                colors={TEXT_COLORS}
                defaultTitle="Couleur par défaut"
                onReset={resetTextColor}
                onSelect={(color) => execFormat("foreColor", color)}
              />
              <ColorMenu
                title="Surligner"
                icon={IconHighlighter}
                colors={HIGHLIGHT_COLORS}
                defaultTitle="Aucun surlignage"
                onReset={resetHighlight}
                onSelect={toggleHighlight}
              />
            </>
          )}
        </Fragment>
      ))}
    </div>
  );
}
