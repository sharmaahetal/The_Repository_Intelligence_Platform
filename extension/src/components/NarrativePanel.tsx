import React from 'react';

interface NarrativePanelProps {
  summary: string;
}

export const NarrativePanel: React.FC<NarrativePanelProps> = ({ summary }) => {
  if (!summary) return null;

  return (
    <div
      style={{
        marginTop: '10px',
        backgroundColor: '#161b22',
        border: '1px solid #21262d',
        borderRadius: '6px',
        padding: '10px 12px',
        fontSize: '12px',
        lineHeight: 1.45,
        color: '#c9d1d9',
      }}
      aria-label="Repository Narrative Summary"
    >
      <div style={{ fontSize: '10px', fontWeight: 600, color: '#58a6ff', marginBottom: '4px', textTransform: 'uppercase' }}>
        🤖 AI Repository Narrative
      </div>
      <div>{summary}</div>
    </div>
  );
};
