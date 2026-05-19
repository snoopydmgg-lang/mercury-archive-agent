import React from 'react';
import {
  useCurrentFrame,
  interpolate,
  AbsoluteFill,
} from 'remotion';

const COLORS = {
  accent: '#D36B4D',
  ink: '#2D2B2A',
};

export function Transition() {
  const frame = useCurrentFrame();

  const slideIn = interpolate(frame, [0, 7], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const slideOut = interpolate(frame, [8, 15], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  let translateX: number;
  if (frame <= 7) {
    translateX = -100 + slideIn * 100;
  } else {
    translateX = slideOut * 100;
  }

  return (
    <AbsoluteFill
      style={{
        width: '100%',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: COLORS.accent,
          transform: [{ translateX: `${translateX}%` }],
          boxShadow: '0 0 80px rgba(45, 43, 42, 0.15)',
        }}
      />
    </AbsoluteFill>
  );
}
