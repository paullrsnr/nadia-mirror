import type { ComponentType } from "react";
import type { LabeledOption } from "./LabeledOption";

export interface ColorMenuProps {
  title: string;
  icon: ComponentType;
  colors: LabeledOption[];
  defaultTitle: string;
  onReset: () => void;
  onSelect: (color: string) => void;
}
