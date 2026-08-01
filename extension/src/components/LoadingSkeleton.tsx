import React from 'react';

export const LoadingSkeleton: React.FC = () => {
  return (
    <div
      style={{
        background: 'rgba(13, 17, 23, 0.95)',
        border: '1px solid rgba(48, 54, 61, 0.8)',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '16px',
        color: '#c9d1d9',
      }}
      aria-label="Loading repository forecast"
      aria-busy="true"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ width: '140px', height: '14px', backgroundColor: '#21262d', borderRadius: '4px' }} />
        <div style={{ width: '60px', height: '18px', backgroundColor: '#21262d', borderRadius: '12px' }} />
      </div>
      <div style={{ width: '100%', height: '12px', backgroundColor: '#21262d', borderRadius: '4px', marginBottom: '8px' }} />
      <div style={{ width: '80%', height: '12px', backgroundColor: '#21262d', borderRadius: '4px', marginBottom: '12px' }} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
        <div style={{ height: '45px', backgroundColor: '#161b22', borderRadius: '6px' }} />
        <div style={{ height: '45px', backgroundColor: '#161b22', borderRadius: '6px' }} />
        <div style={{ height: '45px', backgroundColor: '#161b22', borderRadius: '6px' }} />
      </div>
    </div>
  );
};
