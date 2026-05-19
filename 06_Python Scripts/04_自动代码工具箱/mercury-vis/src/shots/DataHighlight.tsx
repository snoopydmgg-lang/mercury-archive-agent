import React from 'react';
import {
  useCurrentFrame,
  interpolate,
  spring,
  AbsoluteFill,
} from 'remotion';

const FONT = '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif';

export function DataHighlight({
  number,
  unit,
  description,
  bg_color = '#0f3460',
  text_color = '#ffffff',
  accent_color = '#e94560',
  duration_sec = 3,
}: {
  number: string;
  unit: string;
  description?: string;
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  duration_sec?: number;
}) {
  const frame = useCurrentFrame();
  const fps = 30;
  const totalFrames = duration_sec * fps;

  // Bouncy scale for number
  const numberSpring = spring({
    frame,
    fps,
    config: {
      damping: 8,
      stiffness: 100,
    },
  });

  // Fade in for unit
  const unitProgress = interpolate(
    frame,
    [Math.floor(totalFrames * 0.4), Math.floor(totalFrames * 0.7)],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Fade in for description
  const descProgress = interpolate(
    frame,
    [Math.floor(totalFrames * 0.6), Math.floor(totalFrames * 0.9)],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: bg_color }}>
      {/* Number with bouncy effect - centered for horizontal */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `translate(-50%, -50%) scale(${numberSpring})`,
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontFamily: FONT,
            color: accent_color,
            fontSize: 220,
            fontWeight: 800,
            lineHeight: 1,
          }}
        >
          {number}
        </div>

        {/* Unit */}
        <div
          style={{
            fontFamily: FONT,
            color: text_color,
            fontSize: 56,
            fontWeight: 400,
            letterSpacing: '0.25em',
            marginTop: 12,
            opacity: unitProgress,
            transform: `translateY(${(1 - unitProgress) * 25}px)`,
          }}
        >
          {unit}
        </div>

        {/* Description */}
        {description && (
          <div
            style={{
              fontFamily: FONT,
              color: text_color,
              fontSize: 28,
              fontWeight: 400,
              letterSpacing: '0.15em',
              marginTop: 20,
              opacity: descProgress,
              transform: `translateY(${(1 - descProgress) * 20}px)`,
            }}
          >
            {description}
          </div>
        )}
      </div>

      {/* Decorative circles */}
      <div
        style={{
          position: 'absolute',
          top: '15%',
          right: '12%',
          width: 100,
          height: 100,
          borderRadius: '50%',
          border: `3px solid ${accent_color}`,
          opacity: 0.3,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '20%',
          left: '8%',
          width: 50,
          height: 50,
          borderRadius: '50%',
          backgroundColor: accent_color,
          opacity: 0.2,
        }}
      />
    </AbsoluteFill>
  );
}
