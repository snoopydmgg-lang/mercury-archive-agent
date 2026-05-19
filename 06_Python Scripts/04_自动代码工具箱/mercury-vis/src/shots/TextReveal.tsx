import React from 'react';
import {
  useCurrentFrame,
  interpolate,
  AbsoluteFill,
} from 'remotion';

const FONT = '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif';

export function TextReveal({
  text_main,
  text_sub,
  bg_color = '#1a1a2e',
  text_color = '#ffffff',
  duration_sec = 4,
}: {
  text_main: string;
  text_sub: string;
  bg_color?: string;
  text_color?: string;
  duration_sec?: number;
}) {
  const frame = useCurrentFrame();
  const fps = 30;
  const totalFrames = duration_sec * fps;

  // Main text: fade in from below
  const mainProgress = interpolate(frame, [0, totalFrames / 2], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Sub text: delayed fade in
  const subProgress = interpolate(
    frame,
    [Math.floor(totalFrames * 0.3), Math.floor(totalFrames * 0.8)],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Line decoration: grows from center
  const lineProgress = interpolate(frame, [0, totalFrames / 3], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: bg_color }}>
      {/* Main Title - centered for horizontal */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `translate(-50%, -50%) translateY(${(1 - mainProgress) * 50}px)`,
          opacity: mainProgress,
          textAlign: 'center',
          width: '80%',
        }}
      >
        <div
          style={{
            fontFamily: FONT,
            color: text_color,
            fontSize: 96,
            fontWeight: 700,
            lineHeight: 1.1,
            marginBottom: 20,
          }}
        >
          {text_main}
        </div>

        {/* Decorative Line */}
        <div
          style={{
            width: `${lineProgress * 160}px`,
            height: 3,
            backgroundColor: text_color,
            margin: '0 auto 20px',
            opacity: mainProgress * 0.6,
          }}
        />

        {/* Subtitle */}
        <div
          style={{
            fontFamily: FONT,
            color: text_color,
            fontSize: 36,
            fontWeight: 400,
            letterSpacing: '0.15em',
            opacity: subProgress,
            transform: `translateY(${(1 - subProgress) * 25}px)`,
          }}
        >
          {text_sub}
        </div>
      </div>
    </AbsoluteFill>
  );
}
