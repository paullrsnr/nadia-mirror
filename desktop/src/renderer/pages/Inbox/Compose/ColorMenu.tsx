import { useState } from "react";
import { preventBlur } from "../../../helpers";
import type { ColorMenuProps } from "../../../models";

export default function ColorMenu({ title, icon: Icon, colors, defaultTitle, onReset, onSelect }: ColorMenuProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="compose-toolbar__color-wrap">
      <button
        type="button"
        className="compose-toolbar__btn"
        onMouseDown={preventBlur}
        onClick={() => setOpen((o) => !o)}
        title={title}
      >
        <Icon />
      </button>
      {open && (
        <>
          <div className="compose-toolbar__color-backdrop" onClick={() => setOpen(false)} />
          <div className="compose-toolbar__color-menu">
            <button
              type="button"
              className="compose-toolbar__color-swatch compose-toolbar__color-swatch--default"
              title={defaultTitle}
              onMouseDown={preventBlur}
              onClick={() => {
                onReset();
                setOpen(false);
              }}
            />
            {colors.map((color) => (
              <button
                key={color.value}
                type="button"
                className="compose-toolbar__color-swatch"
                style={{ backgroundColor: color.value }}
                title={color.label}
                onMouseDown={preventBlur}
                onClick={() => {
                  onSelect(color.value);
                  setOpen(false);
                }}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
