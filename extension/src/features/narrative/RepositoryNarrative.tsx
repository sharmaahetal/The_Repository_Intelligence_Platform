import React from 'react';

interface RepositoryNarrativeProps {
  summary: string;
  drivers: string[];
  risks: string[];
}

export const RepositoryNarrative: React.FC<RepositoryNarrativeProps> = ({
  summary,
  drivers,
  risks,
}) => {
  return (
    <div style={{ marginTop: '12px', fontSize: '13px', color: 'var(--rip-text-primary)' }}>
      <p style={{ margin: '0 0 10px 0', lineHeight: 1.4 }}>{summary}</p>

      {drivers.length > 0 && (
        <div style={{ marginBottom: '8px' }}>
          <strong style={{ color: 'var(--rip-accent-green)', fontSize: '12px' }}>🟢 Positive Drivers:</strong>
          <ul style={{ margin: '4px 0 0 18px', padding: 0, fontSize: '12px' }}>
            {drivers.map((d, i) => (
              <li key={i}>{d}</li>
            ))}
          </ul>
        </div>
      )}

      {risks.length > 0 && (
        <div>
          <strong style={{ color: 'var(--rip-accent-red)', fontSize: '12px' }}>🔴 Risk Factors:</strong>
          <ul style={{ margin: '4px 0 0 18px', padding: 0, fontSize: '12px' }}>
            {risks.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
