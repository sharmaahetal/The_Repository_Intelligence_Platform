import { ForecastResponseDTO } from '../types/api_dto';
import { ForecastUIModel } from '../types/ui_model';

export function mapForecastDtoToUiModel(dto: ForecastResponseDTO): ForecastUIModel {
  const details = dto.forecast;

  const growthProb = details?.growth_probability ?? dto.growth_probability ?? 0.0;
  const abandonProb = details?.abandonment_probability ?? dto.abandonment_probability ?? 0.0;
  const retentionProb = details?.maintainer_retention_probability ?? dto.maintainer_retention_probability ?? 0.0;
  const healthIdx = details?.derived_health_index ?? dto.derived_health_index ?? Math.round(growthProb * 100);

  return {
    predictionId: dto.prediction_id || `pred_${Math.random().toString(36).substring(2, 10)}`,
    repository: dto.repository || `${dto.owner}/${dto.repo}`,
    owner: dto.owner,
    repo: dto.repo,
    predictionHorizonDays: dto.prediction_horizon_days || 180,
    predictionTime: dto.prediction_time || new Date().toISOString(),
    snapshotTime: dto.snapshot_time || new Date().toISOString(),
    modelVersion: dto.model_version || 'v1.0',
    growthProbability: Math.round(growthProb * 100) / 100,
    abandonmentProbability: Math.round(abandonProb * 100) / 100,
    maintainerRetentionProbability: Math.round(retentionProb * 100) / 100,
    healthIndex: healthIdx,
    confidence: dto.confidence || 0.85,
    topFactors: (dto.top_factors || []).map((f) => ({
      name: f.name,
      impact: f.impact,
      description: f.description,
    })),
    narrativeSummary: dto.narrative_summary || 'No narrative summary available.',
    topDrivers: dto.top_drivers || [],
    topRisks: dto.top_risks || [],
    isCached: Boolean(dto.cached),
    latencyMs: dto.latency_ms || 0,
  };
}
