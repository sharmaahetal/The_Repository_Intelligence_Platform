import { create } from 'zustand';

export interface ForecastData {
  owner: string;
  repo: string;
  predictionHorizonDays: number;
  healthIndex: number;
  growthProbability: number;
  expectedStarGrowthPercent: number;
  abandonmentProbability: number;
  maintainerRetentionProbability: number;
  narrativeSummary: string;
  topDrivers: string[];
  topRisks: string[];
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

  setRepo: (owner, repo) => set({ currentRepo: { owner, repo } }),
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
      // Stub for API endpoint integration
      const mockForecast: ForecastData = {
        owner,
        repo,
        predictionHorizonDays: horizon,
        healthIndex: 88,
        growthProbability: 0.84,
        expectedStarGrowthPercent: 34,
        abandonmentProbability: 0.06,
        maintainerRetentionProbability: 0.91,
        narrativeSummary: `This repository (${owner}/${repo}) is likely to continue growing over the next ${horizon} days. Driven by sustained contributor retention and consistent release cadence.`,
        topDrivers: [
          'Sustained core contributor retention (91%)',
          'High pull request merge turnaround velocity',
          'Consistent tagged release rhythm',
        ],
        topRisks: [
          'Minor slowdown in 30-day commit acceleration',
        ],
      };
      set({ forecast: mockForecast, loading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch forecast report', loading: false });
    }
  },
}));
