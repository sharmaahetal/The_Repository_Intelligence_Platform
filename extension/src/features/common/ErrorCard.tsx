import React from 'react';

interface ErrorCardProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorCard: React.FC<ErrorCardProps> = ({ message, onRetry }) => {
  return (
    <div
      style={{
        padding: '16px',
        backgroundColor: 'var(--rip-accent-red-bg, #ffebe9)',
        color: 'var(--rip-accent-red, #cf222e)',
        border: '1px solid var(--rip-border-color, #d0d7de)',
        borderRadius: 'var(--rip-radius, 8px)',
        fontSize: '13px',
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: '6px' }}>Forecast Execution Error</div>
      <div>{message}</div>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: '10px',
            padding: '4px 10px',
            fontSize: '12px',
            borderRadius: '4px',
            border: '1px solid var(--rip-accent-red)',
            backgroundColor: 'var(--rip-bg-primary)',
            color: 'var(--rip-accent-red)',
            cursor: 'pointer',
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
};
