import React from 'react';

interface ConfidenceBadgeProps {
  confidence: number;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence }) => {
  const percentage = Math.round(confidence * 100);
  const color = percentage >= 80 ? 'var(--rip-accent-green, #1a7f37)' : 'var(--rip-accent-amber, #9a6700)';
  const bgColor = percentage >= 80 ? 'var(--rip-accent-green-bg, #dafbe1)' : 'var(--rip-accent-amber-bg, #fff8c5)';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 600,
        color,
        backgroundColor: bgColor,
        border: `1px solid ${color}40`,
      }}
    >
      {percentage}% Confidence
    </span>
  );
};
