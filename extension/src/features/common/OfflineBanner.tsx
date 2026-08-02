import React from 'react';

interface OfflineBannerProps {
  lastCachedAt?: string | null;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({ lastCachedAt }) => {
  const formattedTime = lastCachedAt
    ? new Date(lastCachedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : 'previously';

  return (
    <div
      style={{
        backgroundColor: 'var(--rip-accent-amber-bg, #fff8c5)',
        color: 'var(--rip-accent-amber, #9a6700)',
        border: '1px solid var(--rip-border-color, #d0d7de)',
        borderRadius: '6px',
        padding: '8px 12px',
        fontSize: '12px',
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}
    >
      <span style={{ fontSize: '14px' }}>⚠️</span>
      <div>
        <strong>Backend Unreachable.</strong> Displaying cached forecast from {formattedTime}.
      </div>
    </div>
  );
};
