import React from 'react';
import { useForecastStore } from '../../state/useForecastStore';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { ErrorCard } from '../common/ErrorCard';
import { LoadingSkeleton } from '../common/LoadingSkeleton';
import { OfflineBanner } from '../common/OfflineBanner';
import { SHAPPanel } from '../explainability/SHAPPanel';
import { RepositoryNarrative } from '../narrative/RepositoryNarrative';

export const ForecastCard: React.FC = () => {
  const { forecast, loading, error, isOffline, lastCachedAt, setHorizonDays, horizonDays, currentRepo, fetchForecast } =
    useForecastStore();

  if (loading && !forecast) {
    return <LoadingSkeleton />;
  }

  if (error && !forecast) {
    return (
      <ErrorCard
        message={error}
        onRetry={() => currentRepo && fetchForecast(currentRepo.owner, currentRepo.repo, horizonDays)}
      />
    );
  }

  if (!forecast) return null;

  return (
    <div
      style={{
        padding: '16px',
        backgroundColor: 'var(--rip-bg-primary, #ffffff)',
        border: '1px solid var(--rip-border-color, #d0d7de)',
        borderRadius: 'var(--rip-radius, 8px)',
        boxShadow: 'var(--rip-shadow)',
        marginBottom: '16px',
        fontFamily: 'var(--rip-font-family)',
      }}
    >
      {isOffline && <OfflineBanner lastCachedAt={lastCachedAt} />}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div>
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--rip-text-primary)' }}>
            📊 Repository Health Index
          </div>
          <div style={{ fontSize: '11px', color: 'var(--rip-text-secondary)' }}>
            Model {forecast.modelVersion} | {forecast.predictionHorizonDays}d Horizon
          </div>
        </div>
        <ConfidenceBadge confidence={forecast.confidence} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <div
          style={{
            fontSize: '28px',
            fontWeight: 700,
            color: forecast.healthIndex >= 70 ? 'var(--rip-accent-green)' : 'var(--rip-accent-amber)',
          }}
        >
          {forecast.healthIndex}/100
        </div>
        <div style={{ fontSize: '12px', color: 'var(--rip-text-secondary)' }}>
          Growth: {Math.round(forecast.growthProbability * 100)}% | Retention: {Math.round(forecast.maintainerRetentionProbability * 100)}%
        </div>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
        {[90, 180, 365].map((h) => (
          <button
            key={h}
            onClick={() => setHorizonDays(h)}
            style={{
              padding: '2px 8px',
              fontSize: '11px',
              borderRadius: '4px',
              border: '1px solid var(--rip-border-color)',
              backgroundColor: horizonDays === h ? 'var(--rip-accent-blue-bg)' : 'var(--rip-bg-secondary)',
              color: horizonDays === h ? 'var(--rip-accent-blue)' : 'var(--rip-text-primary)',
              cursor: 'pointer',
              fontWeight: horizonDays === h ? 600 : 400,
            }}
          >
            {h}d Horizon
          </button>
        ))}
      </div>

      <RepositoryNarrative
        summary={forecast.narrativeSummary}
        drivers={forecast.topDrivers}
        risks={forecast.topRisks}
      />

      <SHAPPanel factors={forecast.topFactors} />
    </div>
  );
};
