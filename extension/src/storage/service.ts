import { getBrowserAPI } from '../utils/browser';

interface CacheEntry<T> {
  timestamp: number;
  data: T;
}

export class StorageService {
  private ttlMs: number;

  constructor(ttlMinutes: number = 15) {
    this.ttlMs = ttlMinutes * 60 * 1000;
  }

  public async getCachedForecast<T>(owner: string, repo: string, horizon: number): Promise<T | null> {
    const api = getBrowserAPI();
    const key = `forecast_${owner.toLowerCase()}_${repo.toLowerCase()}_${horizon}`;

    return new Promise((resolve) => {
      api.storage.local.get([key], (result) => {
        const entry: CacheEntry<T> | undefined = result[key];
        if (entry && Date.now() - entry.timestamp <= this.ttlMs) {
          resolve(entry.data);
        } else {
          resolve(null);
        }
      });
    });
  }

  public async setCachedForecast<T>(owner: string, repo: string, horizon: number, data: T): Promise<void> {
    const api = getBrowserAPI();
    const key = `forecast_${owner.toLowerCase()}_${repo.toLowerCase()}_${horizon}`;
    const entry: CacheEntry<T> = { timestamp: Date.now(), data };

    return new Promise((resolve) => {
      api.storage.local.set({ [key]: entry }, () => resolve());
    });
  }

  public async clearCache(): Promise<void> {
    const api = getBrowserAPI();
    return new Promise((resolve) => {
      api.storage.local.clear(() => resolve());
    });
  }
}
