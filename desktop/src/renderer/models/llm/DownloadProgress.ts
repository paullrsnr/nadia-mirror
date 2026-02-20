/** Progression d'un téléchargement (percent, loaded, total). */
export interface DownloadProgress {
  percent: number;
  loaded: number;
  total: number;
}
