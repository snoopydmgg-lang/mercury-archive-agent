import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

export const CompositionLinesAnimation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const horizontalLine1Progress = interpolate(frame, [0, fps * 1], [0, 1], { extrapolateRight: 'clamp' });
  const horizontalLine2Progress = interpolate(frame, [fps * 0.5, fps * 1.5], [0, 1], { extrapolateRight: 'clamp' });
  const verticalLine1Progress = interpolate(frame, [fps * 1, fps * 2], [0, 1], { extrapolateRight: 'clamp' });
  const verticalLine2Progress = interpolate(frame, [fps * 1.5, fps * 2.5], [0, 1], { extrapolateRight: 'clamp' });
  const pointsOpacity = interpolate(frame, [fps * 3, fps * 4], [0, 1], { extrapolateRight: 'clamp' });
  const labelOpacity = interpolate(frame, [fps * 7, fps * 8], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ backgroundColor: '#F5F4F0' }}>
      <svg width="100%" height="100%" viewBox="0 0 1080 1920">
        <line x1="0" y1="640" x2={1080 * horizontalLine1Progress} y2="640" stroke="#D36B4D" strokeWidth="4" strokeDasharray="10,5" />
        <line x1="0" y1="1280" x2={1080 * horizontalLine2Progress} y2="1280" stroke="#D36B4D" strokeWidth="4" strokeDasharray="10,5" />
        <line x1="360" y1="0" x2="360" y2={1920 * verticalLine1Progress} stroke="#D36B4D" strokeWidth="4" strokeDasharray="10,5" />
        <line x1="720" y1="0" x2="720" y2={1920 * verticalLine2Progress} stroke="#D36B4D" strokeWidth="4" strokeDasharray="10,5" />
        <circle cx="360" cy="640" r="20" fill="#D36B4D" opacity={pointsOpacity} />
        <circle cx="720" cy="640" r="20" fill="#D36B4D" opacity={pointsOpacity} />
        <circle cx="360" cy="1280" r="20" fill="#D36B4D" opacity={pointsOpacity} />
        <circle cx="720" cy="1280" r="20" fill="#D36B4D" opacity={pointsOpacity} />
      </svg>

      <div style={{ position: 'absolute', top: '10%', left: '50%', transform: 'translateX(-50%)', opacity: labelOpacity }}>
        <div style={{ fontSize: 48, fontWeight: 700, color: '#2D2B2A', textAlign: 'center', fontFamily: 'Georgia, serif' }}>
          三分法构图
        </div>
        <div style={{ fontSize: 28, color: '#2D2B2A', textAlign: 'center', marginTop: 20 }}>
          将主体放在交点上 画面更有张力
        </div>
      </div>
    </AbsoluteFill>
  );
};
