import { ForecastPayload } from '../messaging/types';

export class RepositoryForecastApi {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
  }

  public async getForecast(owner: string, repo: string, horizon: number = 180): Promise<ForecastPayload> {
    const url = `${this.baseUrl}/forecast/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}?horizon=${horizon}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown network error');
      throw new Error(`API Error [HTTP ${response.status}]: ${errorText}`);
    }

    return response.json();
  }

  public async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health/live`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
