import React from 'react';
import { ForecastPayload } from '../messaging/types';
import { ConfidenceBadge } from './ConfidenceBadge';
import { ErrorCard } from './ErrorCard';
import { LoadingSkeleton } from './LoadingSkeleton';
import { NarrativePanel } from './NarrativePanel';
import { SHAPPanel } from './SHAPPanel';

interface ForecastCardProps {
  payload: ForecastPayload | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

export const ForecastCard: React.FC<ForecastCardProps> = ({
  payload,
  loading,
  error,
  onRetry,
}) => {
  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorCard message={error} onRetry={onRetry} />;
  if (!payload) return null;

  const { forecast, top_factors, narrative_summary } = payload;
  const growthPct = Math.round(forecast.growth_probability * 100);
  const abandonPct = Math.round(forecast.abandonment_probability * 100);

  return (
    <div
      style={{
        background: 'rgba(13, 17, 23, 0.95)',
        border: '1px solid rgba(48, 54, 61, 0.8)',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '16px',
        color: '#c9d1d9',
        fontFamily: "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif",
      }}
    >
      {/* Header & Confidence Badge */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid #30363d',
          paddingBottom: '8px',
          marginBottom: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontWeight: 600, color: '#58a6ff', fontSize: '14px' }}>
            ⚡ Repository Intelligence Forecast
          </span>
          {payload.cached && (
            <span
              style={{
                fontSize: '9px',
                color: '#8b949e',
                border: '1px solid #30363d',
                padding: '1px 5px',
                borderRadius: '4px',
              }}
            >
              CACHED
            </span>
          )}
        </div>
        <ConfidenceBadge
          growthProbability={forecast.growth_probability}
          abandonmentProbability={forecast.abandonment_probability}
        />
      </div>

      {/* Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', textAlign: 'center' }}>
        <div style={{ background: '#161b22', padding: '8px', borderRadius: '6px', border: '1px solid #21262d' }}>
          <div style={{ fontSize: '10px', color: '#8b949e' }}>Health Index</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#3fb950' }}>
            {forecast.derived_health_index} / 100
          </div>
        </div>
        <div style={{ background: '#161b22', padding: '8px', borderRadius: '6px', border: '1px solid #21262d' }}>
          <div style={{ fontSize: '10px', color: '#8b949e' }}>Growth Prob</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#58a6ff' }}>
            {growthPct}%
          </div>
        </div>
        <div style={{ background: '#161b22', padding: '8px', borderRadius: '6px', border: '1px solid #21262d' }}>
          <div style={{ fontSize: '10px', color: '#8b949e' }}>Abandon Risk</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#f85149' }}>
            {abandonPct}%
          </div>
        </div>
      </div>

      {/* Narrative Section */}
      <NarrativePanel summary={narrative_summary} />

      {/* SHAP Impact Analysis */}
      <SHAPPanel factors={top_factors} />
    </div>
  );
};
