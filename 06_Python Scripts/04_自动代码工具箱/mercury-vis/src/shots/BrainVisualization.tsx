import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

interface BrainVisualizationProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function BrainVisualization({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '大脑视觉感知',
  text_sub = '中心区高亮 · 周边逐渐变暗',
}: BrainVisualizationProps) {
  const frame = useCurrentFrame();

  // 中心圆扩散动画
  const centerScale = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  // 周边圆圈逐渐变暗
  const outerOpacity = interpolate(frame, [30, 60], [1, 0.3], {
    extrapolateRight: 'clamp',
  });

  // 文字淡入
  const textOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: bg_color }}>
      {/* SVG 图形 */}
      <svg
        width="1920"
        height="1080"
        viewBox="0 0 1920 1080"
        style={{ position: 'absolute' }}
      >
        {/* 噪点纹理滤镜 */}
        <defs>
          <filter id="noise">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.7"
              numOctaves="3"
              stitchTiles="stitch"
            />
            <feColorMatrix
              type="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.032 0"
            />
          </filter>
        </defs>

        {/* 背景噪点 */}
        <rect width="1920" height="1080" filter="url(#noise)" />

        {/* 中心高亮区域 */}
        <circle
          cx="960"
          cy="540"
          r={150 * centerScale}
          fill={accent_color}
          opacity="0.8"
        />

        {/* 周边圆圈 - 逐渐变暗 */}
        {[250, 350, 450, 550].map((radius, index) => (
          <circle
            key={radius}
            cx="960"
            cy="540"
            r={radius * centerScale}
            fill="none"
            stroke={text_color}
            strokeWidth="2"
            opacity={outerOpacity * (1 - index * 0.2)}
          />
        ))}

        {/* 视觉焦点指示线 */}
        {frame > 30 &&
          [0, 45, 90, 135, 180, 225, 270, 315].map((angle) => {
            const rad = (angle * Math.PI) / 180;
            const x1 = 960 + Math.cos(rad) * 150;
            const y1 = 540 + Math.sin(rad) * 150;
            const x2 = 960 + Math.cos(rad) * 250;
            const y2 = 540 + Math.sin(rad) * 250;
            return (
              <line
                key={angle}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={accent_color}
                strokeWidth="1"
                opacity={interpolate(frame, [30, 60], [0, 0.6], {
                  extrapolateRight: 'clamp',
                })}
              />
            );
          })}
      </svg>

      {/* 文字说明 */}
      <div
        style={{
          position: 'absolute',
          top: '80px',
          left: '0',
          right: '0',
          textAlign: 'center',
          opacity: textOpacity,
        }}
      >
        <h1
          style={{
            fontFamily:
              "'Source Han Serif SC', 'Noto Serif CJK SC', 'Microsoft YaHei', Georgia, serif",
            fontSize: '72px',
            fontWeight: 600,
            color: text_color,
            margin: 0,
            letterSpacing: '4px',
          }}
        >
          {text_main}
        </h1>
        <p
          style={{
            fontFamily: "'Microsoft YaHei', '微软雅黑', Inter, sans-serif",
            fontSize: '36px',
            color: accent_color,
            margin: '20px 0 0 0',
            letterSpacing: '2px',
          }}
        >
          {text_sub}
        </p>
      </div>
    </AbsoluteFill>
  );
}
