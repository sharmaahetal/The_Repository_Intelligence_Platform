export interface TopFactorDTO {
  name: string;
  impact: number;
  description: string;
}

export interface ForecastDetailsDTO {
  growth_probability: number;
  abandonment_probability: number;
  maintainer_retention_probability: number;
  derived_health_index: number;
}

export interface ForecastResponseDTO {
  prediction_id?: string;
  repository: string;
  owner: string;
  repo: string;
  prediction_horizon_days: number;
  prediction_time: string;
  snapshot_time: string;
  model_version: string;
  feature_schema_version?: number;
  label_schema_version?: number;
  forecast?: ForecastDetailsDTO;

  // Flattened fallbacks
  derived_health_index?: number;
  growth_probability?: number;
  abandonment_probability?: number;
  maintainer_retention_probability?: number;

  confidence?: number;
  top_factors?: TopFactorDTO[];
  narrative_summary?: string;
  top_drivers?: string[];
  top_risks?: string[];
  cached?: boolean;
  latency_ms?: number;
}
