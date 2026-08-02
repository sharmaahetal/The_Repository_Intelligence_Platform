import { create } from 'zustand';
import { fetchForecastReport } from '../services/api';
import { mapForecastDtoToUiModel } from '../services/mapper';
import { getStoredForecast, setStoredForecast } from '../services/storage';
import { ForecastUIModel } from '../types/ui_model';

interface ForecastState {
  currentRepo: { owner: string; repo: string } | null;
  horizonDays: number;
  forecast: ForecastUIModel | null;
  loading: boolean;
  error: string | null;
  isOffline: boolean;
  lastCachedAt: string | null;

  setRepo: (owner: string, repo: string) => void;
  setHorizonDays: (days: number) => void;
  fetchForecast: (owner: string, repo: string, horizon: number) => Promise<void>;
  clearError: () => void;
}

export const useForecastStore = create<ForecastState>((set, get) => ({
  currentRepo: null,
  horizonDays: 180,
  forecast: null,
  loading: false,
  error: null,
  isOffline: false,
  lastCachedAt: null,

  setRepo: (owner, repo) => {
    set({ currentRepo: { owner, repo } });
    get().fetchForecast(owner, repo, get().horizonDays);
  },

  setHorizonDays: (days) => {
    set({ horizonDays: days });
    const { currentRepo } = get();
    if (currentRepo) {
      get().fetchForecast(currentRepo.owner, currentRepo.repo, days);
    }
  },

  clearError: () => set({ error: null }),

  fetchForecast: async (owner, repo, horizon) => {
    set({ loading: true, error: null, isOffline: false });

    // 1. Check extension storage cache (valid TTL)
    const cached = await getStoredForecast(owner, repo, horizon);
    if (cached && !cached.isStale) {
      set({
        forecast: cached.forecast,
        loading: false,
        isOffline: false,
        lastCachedAt: cached.forecast.cachedTimestamp || null,
      });
      return;
    }

    // 2. Fetch from backend API
    try {
      const dto = await fetchForecastReport(owner, repo, horizon);
      const uiModel = mapForecastDtoToUiModel(dto);

      // Save to storage cache
      await setStoredForecast(owner, repo, horizon, uiModel);

      set({
        forecast: uiModel,
        loading: false,
        isOffline: false,
        lastCachedAt: null,
      });
    } catch (err: any) {
      console.warn('[RIP Extension] Backend API fetch failed, checking offline fallback cache:', err);

      // 3. Fallback to stale storage entry if offline
      const staleCached = await getStoredForecast(owner, repo, horizon, true);
      if (staleCached) {
        set({
          forecast: staleCached.forecast,
          loading: false,
          isOffline: true,
          lastCachedAt: staleCached.forecast.cachedTimestamp || new Date().toISOString(),
          error: null,
        });
      } else {
        set({
          error: err.message || 'Failed to fetch repository forecast',
          loading: false,
          isOffline: true,
          lastCachedAt: null,
        });
      }
    }
  },
}));
