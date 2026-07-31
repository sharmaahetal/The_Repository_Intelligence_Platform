export interface ForecastApiResponse {
  owner: string;
  repo: string;
  prediction_horizon_days: number;
  derived_health_index: number;
  growth_probability: number;
  abandonment_probability: number;
  maintainer_retention_probability: number;
  narrative_summary: string;
  top_drivers: string[];
  top_risks: string[];
  model_version: string;
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function fetchForecastReport(
  owner: string,
  repo: string,
  horizon: number = 180
): Promise<ForecastApiResponse> {
  const url = `${API_BASE_URL}/forecast/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}?horizon=${horizon}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`API Error [HTTP ${response.status}]: Failed to fetch forecast for ${owner}/${repo}`);
  }

  return response.json();
}
