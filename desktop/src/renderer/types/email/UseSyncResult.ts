export interface UseSyncResult {
  syncing: boolean;
  syncError: string | null;
  sync: (full?: boolean) => Promise<void>;
}
