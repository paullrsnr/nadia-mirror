/** Entrée du catalogue de modèles téléchargeables (HuggingFace). */
export interface CatalogModel {
  id: string;
  name: string;
  repo: string;
  filename: string;
  description: string;
  category: string;
}
