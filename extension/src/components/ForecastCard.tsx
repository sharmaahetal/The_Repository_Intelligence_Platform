import React from 'react';
import { useForecastStore } from '../state/useForecastStore';

export const ForecastCard: React.FC = () => {
  const { forecast, horizonDays, setHorizonDays, loading, error } = useForecastStore();

  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={{ color: '#8b949e', fontSize: '13px' }}>⚡ Fetching repository forecast...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={containerStyle}>
        <div style={{ color: '#f85149', fontSize: '13px' }}>⚠️ {error}</div>
      </div>
    );
  }

  if (!forecast) return null;

  return (
    <div style={containerStyle}>
      {/* Top Header & Horizon Selector */}
      <div style={headerStyle}>
        <div>
          <span style={{ fontWeight: 600, color: '#58a6ff', fontSize: '14px' }}>
            ⚡ Repository Intelligence Forecast
          </span>
        </div>
        <div style={{ display: 'flex', gap: '4px' }}>
          {[90, 180, 365].map((h) => (
            <button
              key={h}
              onClick={() => setHorizonDays(h)}
              style={{
                background: horizonDays === h ? '#238636' : '#21262d',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                padding: '2px 6px',
                fontSize: '10px',
                cursor: 'pointer',
              }}
            >
              {h}d
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', margin: '12px 0' }}>
        <div style={metricBoxStyle}>
          <div style={metricLabelStyle}>Health Index</div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#3fb950' }}>
            {forecast.healthIndex} / 100
          </div>
        </div>
        <div style={metricBoxStyle}>
          <div style={metricLabelStyle}>P(Growth)</div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#58a6ff' }}>
            {Math.round(forecast.growthProbability * 100)}%
          </div>
        </div>
        <div style={metricBoxStyle}>
          <div style={metricLabelStyle}>P(Abandon)</div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#f85149' }}>
            {Math.round(forecast.abandonmentProbability * 100)}%
          </div>
        </div>
      </div>

      {/* Natural Language Narrative Synthesis */}
      <div style={narrativeStyle}>
        💬 {forecast.narrativeSummary}
      </div>

      {/* Top Drivers */}
      <div style={{ marginTop: '10px', fontSize: '12px' }}>
        <div style={{ fontWeight: 600, color: '#3fb950', marginBottom: '4px' }}>Key Growth Drivers:</div>
        <ul style={{ margin: 0, paddingLeft: '16px', color: '#c9d1d9' }}>
          {forecast.topDrivers.map((driver, idx) => (
            <li key={idx}>{driver}</li>
          ))}
        </ul>
      </div>

      {/* Top Risks */}
      <div style={{ marginTop: '8px', fontSize: '12px' }}>
        <div style={{ fontWeight: 600, color: '#f85149', marginBottom: '4px' }}>Risk Factors:</div>
        <ul style={{ margin: 0, paddingLeft: '16px', color: '#c9d1d9' }}>
          {forecast.topRisks.map((risk, idx) => (
            <li key={idx}>{risk}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

const containerStyle: React.CSSProperties = {
  background: 'rgba(13, 17, 23, 0.95)',
  border: '1px solid rgba(48, 54, 61, 0.8)',
  borderRadius: '12px',
  padding: '16px',
  marginBottom: '16px',
  color: '#c9d1d9',
  fontFamily: "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif",
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  borderBottom: '1px solid #30363d',
  paddingBottom: '8px',
};

const metricBoxStyle: React.CSSProperties = {
  background: '#161b22',
  padding: '8px',
  borderRadius: '6px',
  border: '1px solid #21262d',
  textAlign: 'center',
};

const metricLabelStyle: React.CSSProperties = {
  fontSize: '10px',
  color: '#8b949e',
};

const narrativeStyle: React.CSSProperties = {
  background: '#161b22',
  borderLeft: '3px solid #58a6ff',
  padding: '8px 12px',
  borderRadius: '4px',
  fontSize: '12px',
  lineHeight: 1.5,
  color: '#e6edf3',
};
