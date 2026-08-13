const KILO = 1024;
const MEGA = KILO * KILO;

export function formatFileSize(bytes: number): string {
  if (bytes < KILO) return `${bytes} o`;
  if (bytes < MEGA) return `${(bytes / KILO).toFixed(1)} Ko`;
  return `${(bytes / MEGA).toFixed(1)} Mo`;
}
