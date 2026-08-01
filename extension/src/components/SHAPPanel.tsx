import React from 'react';
import { TopFactor } from '../messaging/types';

interface SHAPPanelProps {
  factors: TopFactor[];
}

export const SHAPPanel: React.FC<SHAPPanelProps> = ({ factors }) => {
  if (!factors || factors.length === 0) return null;

  return (
    <div style={{ marginTop: '12px', borderTop: '1px solid #30363d', paddingTop: '10px' }}>
      <div style={{ fontSize: '11px', fontWeight: 600, color: '#8b949e', marginBottom: '8px' }}>
        🔍 SHAP Feature Drivers (Impact Analysis)
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {factors.map((factor, idx) => {
          const isPositive = factor.impact >= 0;
          const absImpact = Math.min(100, Math.abs(factor.impact) * 100);
          const barColor = isPositive ? '#3fb950' : '#f85149';

          return (
            <div key={idx} style={{ fontSize: '11px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#c9d1d9', marginBottom: '2px' }}>
                <span>{factor.name}</span>
                <span style={{ color: barColor, fontWeight: 600 }}>
                  {isPositive ? '+' : ''}{(factor.impact * 100).toFixed(1)}%
                </span>
              </div>
              <div style={{ width: '100%', height: '4px', backgroundColor: '#21262d', borderRadius: '2px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${absImpact}%`,
                    height: '100%',
                    backgroundColor: barColor,
                    borderRadius: '2px',
                    transition: 'width 0.3s ease',
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
