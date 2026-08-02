import React from 'react';

export const LoadingSkeleton: React.FC = () => {
  return (
    <div
      style={{
        padding: '16px',
        backgroundColor: 'var(--rip-bg-primary, #ffffff)',
        border: '1px solid var(--rip-border-color, #d0d7de)',
        borderRadius: 'var(--rip-radius, 8px)',
        marginBottom: '16px',
      }}
    >
      <div
        style={{
          height: '18px',
          width: '60%',
          backgroundColor: 'var(--rip-border-color, #d0d7de)',
          borderRadius: '4px',
          marginBottom: '12px',
          opacity: 0.6,
        }}
      />
      <div
        style={{
          height: '40px',
          width: '100%',
          backgroundColor: 'var(--rip-border-color, #d0d7de)',
          borderRadius: '4px',
          marginBottom: '12px',
          opacity: 0.4,
        }}
      />
      <div
        style={{
          height: '14px',
          width: '80%',
          backgroundColor: 'var(--rip-border-color, #d0d7de)',
          borderRadius: '4px',
          opacity: 0.5,
        }}
      />
    </div>
  );
};
