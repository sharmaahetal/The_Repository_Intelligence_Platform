import { ForecastPayload } from '../messaging/types';
import { sanitizeText } from '../utils/sanitize';

export class RepositoryNarrativeEngine {
  /**
   * Synthesize natural language narrative explanation from forecast probabilities and top SHAP factors.
   */
  public generateNarrative(payload: ForecastPayload): string {
    const growthProb = payload.forecast.growth_probability;
    const abandonProb = payload.forecast.abandonment_probability;
    const healthIndex = payload.forecast.derived_health_index;
    const repoName = sanitizeText(payload.repository || `${payload.owner}/${payload.repo}`);

    let trajectoryHeader = '';
    if (growthProb >= 0.70) {
      trajectoryHeader = `Strong upward trajectory expected for ${repoName}.`;
    } else if (abandonProb >= 0.40) {
      trajectoryHeader = `Increased abandonment risk detected for ${repoName}.`;
    } else {
      trajectoryHeader = `Stable, steady growth maintenance anticipated for ${repoName}.`;
    }

    const healthText = `The derived health index stands at ${healthIndex}/100 with a ${Math.round(growthProb * 100)}% star growth probability over a ${payload.prediction_horizon_days}-day horizon.`;

    const driversText = payload.top_drivers.length > 0
      ? ` Key growth accelerators include: ${payload.top_drivers.slice(0, 2).join(' and ')}.`
      : '';

    return `${trajectoryHeader} ${healthText}${driversText}`;
  }
}
