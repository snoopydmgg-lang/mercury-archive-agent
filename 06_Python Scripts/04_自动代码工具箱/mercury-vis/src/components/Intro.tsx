import React from 'react';
import {
  useCurrentFrame,
  interpolate,
  AbsoluteFill,
} from 'remotion';

const COLORS = {
  bg: '#F5F4F0',
  ink: '#2D2B2A',
  accent: '#D36B4D',
  muted: '#8A8580',
};

const FONTS = {
  serif: '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif',
  sans: '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif',
};

export function Intro({ mainTitle, subTitle, volNumber }: {
  mainTitle: string;
  subTitle: string;
  volNumber: string;
}) {
  const frame = useCurrentFrame();

  const lineProgress = interpolate(frame, [0, 60], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const titleOpacity = interpolate(frame, [10, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const titleY = interpolate(frame, [10, 30], [30, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const subOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const subY = interpolate(frame, [35, 55], [20, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const metaOpacity = interpolate(frame, [25, 45], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      {/* 右上角：期号 */}
      <div
        style={{
          position: 'absolute',
          top: 40,
          right: 60,
          opacity: metaOpacity,
        }}
      >
        <span
          style={{
            fontFamily: FONTS.sans,
            color: COLORS.accent,
            fontSize: 24,
            fontWeight: 400,
            letterSpacing: '0.1em',
          }}
        >
          {volNumber}
        </span>
      </div>

      {/* 左下角：水星艺术馆标识 */}
      <div
        style={{
          position: 'absolute',
          bottom: 60,
          left: 60,
          opacity: metaOpacity,
        }}
      >
        <span
          style={{
            fontFamily: FONTS.sans,
            color: COLORS.ink,
            fontSize: 18,
            marginBottom: 4,
            display: 'block',
          }}
        >
          水星艺术馆
        </span>
        <span
          style={{
            fontFamily: FONTS.sans,
            color: COLORS.muted,
            fontSize: 12,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
          }}
        >
          MERCURY ART ARCHIVE
        </span>
      </div>

      {/* 中央：主标题 + 副标题 */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `translate(-50%, -50%) translateY(${titleY}px)`,
          opacity: titleOpacity,
          textAlign: 'center',
          width: '80%',
        }}
      >
        <span
          style={{
            fontFamily: FONTS.serif,
            color: COLORS.ink,
            fontSize: 80,
            fontWeight: 700,
            lineHeight: 1.1,
            marginBottom: 16,
            display: 'block',
          }}
        >
          {mainTitle}
        </span>
        <span
          style={{
            fontFamily: FONTS.sans,
            color: '#5A5551',
            fontSize: 24,
            fontWeight: 400,
            letterSpacing: '0.05em',
          }}
        >
          {subTitle}
        </span>
      </div>

      {/* 底部：动态分割线 */}
      <div
        style={{
          position: 'absolute',
          bottom: 100,
          left: '10%',
          width: '80%',
          height: 2,
        }}
      >
        <div
          style={{
            width: `${lineProgress}%`,
            height: '100%',
            backgroundColor: COLORS.accent,
          }}
        />
      </div>
    </AbsoluteFill>
  );
}
