import React from 'react';

interface ConfidenceBadgeProps {
  growthProbability: number;
  abandonmentProbability: number;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  growthProbability,
  abandonmentProbability,
}) => {
  let label = 'Steady';
  let bgColor = '#1f6beb';
  let textColor = '#ffffff';

  if (growthProbability >= 0.7) {
    label = 'Growing';
    bgColor = '#238636';
  } else if (abandonmentProbability >= 0.4) {
    label = 'At Risk';
    bgColor = '#da3633';
  }

  return (
    <span
      style={{
        backgroundColor: bgColor,
        color: textColor,
        fontSize: '11px',
        fontWeight: 600,
        padding: '2px 8px',
        borderRadius: '12px',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
      }}
      aria-label={`Status: ${label}`}
    >
      <span>⚡</span> {label}
    </span>
  );
};
