import React from 'react';

interface ErrorCardProps {
  message: string;
  onRetry: () => void;
}

export const ErrorCard: React.FC<ErrorCardProps> = ({ message, onRetry }) => {
  return (
    <div
      style={{
        background: 'rgba(13, 17, 23, 0.95)',
        border: '1px solid #da3633',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '16px',
        color: '#c9d1d9',
        fontSize: '13px',
      }}
      role="alert"
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f85149', fontWeight: 600, marginBottom: '6px' }}>
        <span>⚠️</span> Forecast Unavailable
      </div>
      <div style={{ color: '#8b949e', marginBottom: '10px' }}>{message}</div>
      <button
        onClick={onRetry}
        style={{
          backgroundColor: '#21262d',
          color: '#58a6ff',
          border: '1px solid #30363d',
          borderRadius: '6px',
          padding: '4px 12px',
          fontSize: '12px',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        🔄 Retry Prediction
      </button>
    </div>
  );
};
