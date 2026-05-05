interface BadgeProps {
  label: string;
  className?: string;
}

/**
 * Badge générique — le style visuel est piloté via la classe CSS (global.css).
 * Pour les badges de catégorie email, passer className="category-badge category-badge--{category}".
 */
export default function Badge({ label, className = "category-badge" }: BadgeProps) {
  return <span className={className}>{label}</span>;
}
