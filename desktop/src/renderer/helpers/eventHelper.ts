import type { MouseEvent } from "react";

export function preventBlur(event: MouseEvent): void {
  event.preventDefault();
}
