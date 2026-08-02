export interface TopFactorUI {
  name: string;
  impact: number;
  description: string;
}

export interface ForecastUIModel {
  predictionId: string;
  repository: string;
  owner: string;
  repo: string;
  predictionHorizonDays: number;
  predictionTime: string;
  snapshotTime: string;
  modelVersion: string;
  growthProbability: number;
  abandonmentProbability: number;
  maintainerRetentionProbability: number;
  healthIndex: number;
  confidence: number;
  topFactors: TopFactorUI[];
  narrativeSummary: string;
  topDrivers: string[];
  topRisks: string[];
  isCached: boolean;
  latencyMs: number;
  cachedTimestamp?: string;
}
