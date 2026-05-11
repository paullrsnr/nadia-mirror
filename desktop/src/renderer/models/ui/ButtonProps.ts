import type React from "react";
import type { ButtonSize, ButtonVariant } from "./Button";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}
