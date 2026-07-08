import type { BadgeProps } from "../../../models/ui/BadgeProps";

export default function Badge({ label, className = "category-badge" }: BadgeProps) {
  return <span className={className}>{label}</span>;
}
