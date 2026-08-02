import React from 'react';
import { TopFactorUI } from '../../types/ui_model';

interface SHAPPanelProps {
  factors: TopFactorUI[];
}

export const SHAPPanel: React.FC<SHAPPanelProps> = ({ factors }) => {
  if (!factors || factors.length === 0) return null;

  return (
    <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--rip-border-color)' }}>
      <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--rip-text-secondary)', marginBottom: '8px' }}>
        SHAP Feature Attribution Drivers
      </div>
      {factors.map((f, i) => {
        const isPositive = f.impact >= 0;
        const barColor = isPositive ? 'var(--rip-accent-green)' : 'var(--rip-accent-red)';
        const widthPct = Math.min(100, Math.abs(f.impact) * 100);

        return (
          <div key={i} style={{ marginBottom: '8px', fontSize: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
              <span style={{ fontWeight: 500 }}>{f.name}</span>
              <span style={{ color: barColor, fontWeight: 600 }}>
                {isPositive ? '+' : ''}
                {f.impact.toFixed(2)}
              </span>
            </div>
            <div style={{ height: '4px', width: '100%', backgroundColor: 'var(--rip-border-color)', borderRadius: '2px' }}>
              <div style={{ height: '100%', width: `${widthPct}%`, backgroundColor: barColor, borderRadius: '2px' }} />
            </div>
            <div style={{ fontSize: '11px', color: 'var(--rip-text-secondary)', marginTop: '2px' }}>{f.description}</div>
          </div>
        );
      })}
    </div>
  );
};
