import type { Category } from "./Category";
import type { CategoryChipColors } from "./CategoryChipColors";

export type CategoryChipOverrides = Partial<Record<Category["name"], CategoryChipColors>>;
