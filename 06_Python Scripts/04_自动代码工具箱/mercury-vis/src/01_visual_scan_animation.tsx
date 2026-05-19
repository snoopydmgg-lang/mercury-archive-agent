import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from 'remotion';

export const VisualScanAnimation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const eyeScale = spring({
    frame: frame - 0,
    fps,
    config: { damping: 12 },
  });

  const scanLineProgress = interpolate(
    frame,
    [fps * 1, fps * 3],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  const element1Opacity = interpolate(
    frame,
    [fps * 3, fps * 3.5],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  const element2Opacity = interpolate(
    frame,
    [fps * 3.5, fps * 4],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  const element3Opacity = interpolate(
    frame,
    [fps * 4, fps * 4.5],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  const connectionLineProgress = interpolate(
    frame,
    [fps * 4.5, fps * 7],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: '#F5F4F0' }}>
      <div
        style={{
          position: 'absolute',
          top: '20%',
          left: '50%',
          transform: `translate(-50%, -50%) scale(${eyeScale})`,
        }}
      >
        <svg width="120" height="80" viewBox="0 0 120 80">
          <ellipse cx="60" cy="40" rx="50" ry="30" fill="none" stroke="#2D2B2A" strokeWidth="3" />
          <circle cx="60" cy="40" r="15" fill="#2D2B2A" />
          <circle cx="65" cy="35" r="5" fill="#F5F4F0" />
        </svg>
      </div>

      <svg width="100%" height="100%" style={{ position: 'absolute', top: 0, left: 0 }}>
        <path
          d={`M 60 ${120 + (400 - 120) * scanLineProgress} L 300 ${200 + (500 - 200) * scanLineProgress}`}
          stroke="#D36B4D"
          strokeWidth="3"
          fill="none"
          strokeDasharray="5,5"
        />
      </svg>

      <div
        style={{
          position: 'absolute',
          bottom: '15%',
          left: '50%',
          transform: 'translateX(-50%)',
          fontSize: 24,
          color: '#2D2B2A',
          fontWeight: 600,
          textAlign: 'center',
          opacity: interpolate(frame, [fps * 5, fps * 6], [0, 1], {
            extrapolateRight: 'clamp',
          }),
        }}
      >
        眼睛会被相似元素吸引并沿着线条移动
      </div>
    </AbsoluteFill>
  );
};
