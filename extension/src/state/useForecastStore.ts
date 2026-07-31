import { create } from 'zustand';
import { fetchForecastReport } from '../services/api';

export interface ForecastData {
  owner: string;
  repo: string;
  predictionHorizonDays: number;
  healthIndex: number;
  growthProbability: number;
  abandonmentProbability: number;
  maintainerRetentionProbability: number;
  narrativeSummary: string;
  topDrivers: string[];
  topRisks: string[];
  modelVersion: string;
}

interface ForecastState {
  currentRepo: { owner: string; repo: string } | null;
  horizonDays: number;
  forecast: ForecastData | null;
  loading: boolean;
  error: string | null;

  setRepo: (owner: string, repo: string) => void;
  setHorizonDays: (days: number) => void;
  fetchForecast: (owner: string, repo: string, horizon: number) => Promise<void>;
}

export const useForecastStore = create<ForecastState>((set, get) => ({
  currentRepo: null,
  horizonDays: 180,
  forecast: null,
  loading: false,
  error: null,

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

  fetchForecast: async (owner, repo, horizon) => {
    set({ loading: true, error: null });
    try {
      const apiData = await fetchForecastReport(owner, repo, horizon);
      
      const forecast: ForecastData = {
        owner: apiData.owner,
        repo: apiData.repo,
        predictionHorizonDays: apiData.prediction_horizon_days,
        healthIndex: apiData.derived_health_index,
        growthProbability: apiData.growth_probability,
        abandonmentProbability: apiData.abandonment_probability,
        maintainerRetentionProbability: apiData.maintainer_retention_probability,
        narrativeSummary: apiData.narrative_summary,
        topDrivers: apiData.top_drivers,
        topRisks: apiData.top_risks,
        modelVersion: apiData.model_version,
      };

      set({ forecast, loading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch forecast report', loading: false });
    }
  },
}));
