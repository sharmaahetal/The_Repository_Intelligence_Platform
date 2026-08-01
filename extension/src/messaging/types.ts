export type MessageAction =
  | 'FETCH_FORECAST'
  | 'FORECAST_RESPONSE'
  | 'SETTINGS_UPDATE'
  | 'CLEAR_CACHE'
  | 'ERROR_RESPONSE';

export interface TopFactor {
  name: string;
  impact: number;
  description: string;
}

export interface ForecastPayload {
  repository: string;
  owner: string;
  repo: string;
  prediction_horizon_days: number;
  prediction_time: string;
  snapshot_time: string;
  model_version: string;
  feature_schema_version: number;
  label_schema_version: number;
  forecast: {
    growth_probability: number;
    abandonment_probability: number;
    maintainer_retention_probability: number;
    derived_health_index: number;
  };
  confidence: number;
  top_factors: TopFactor[];
  narrative_summary: string;
  top_drivers: string[];
  top_risks: string[];
  cached: boolean;
}

export interface ExtensionMessage<T = any> {
  action: MessageAction;
  payload?: T;
  error?: string;
}
