import { ForecastResponseDTO } from '../types/api_dto';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function fetchForecastReport(
  owner: string,
  repo: string,
  horizon: number = 180
): Promise<ForecastResponseDTO> {
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
