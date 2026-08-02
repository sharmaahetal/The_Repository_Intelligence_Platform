import { ForecastUIModel } from '../types/ui_model';

const STORAGE_PREFIX = 'rip_forecast_cache_';
const DEFAULT_TTL_MS = 15 * 60 * 1000; // 15 Minutes TTL

interface CachedEntry {
  timestamp: number;
  data: ForecastUIModel;
}

export async function getStoredForecast(
  owner: string,
  repo: string,
  horizon: number = 180,
  ignoreTtl: boolean = false
): Promise<{ forecast: ForecastUIModel; isStale: boolean } | null> {
  const key = `${STORAGE_PREFIX}${owner.toLowerCase()}_${repo.toLowerCase()}_${horizon}`;
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;

    const entry: CachedEntry = JSON.parse(raw);
    const age = Date.now() - entry.timestamp;
    const isStale = age > DEFAULT_TTL_MS;

    if (isStale && !ignoreTtl) {
      return null;
    }

    return {
      forecast: {
        ...entry.data,
        cachedTimestamp: new Date(entry.timestamp).toISOString(),
      },
      isStale,
    };
  } catch (err) {
    console.warn('[RIP Storage] Error reading stored forecast:', err);
    return null;
  }
}

export async function setStoredForecast(
  owner: string,
  repo: string,
  horizon: number,
  data: ForecastUIModel
): Promise<void> {
  const key = `${STORAGE_PREFIX}${owner.toLowerCase()}_${repo.toLowerCase()}_${horizon}`;
  try {
    const entry: CachedEntry = {
      timestamp: Date.now(),
      data,
    };
    localStorage.setItem(key, JSON.stringify(entry));
  } catch (err) {
    console.warn('[RIP Storage] Error saving forecast to storage:', err);
  }
}
