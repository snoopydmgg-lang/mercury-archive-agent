import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

interface EyeTrackingProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function EyeTracking({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '人眼扫描轨迹',
  text_sub = '视线追踪 · 焦点转移',
}: EyeTrackingProps) {
  const frame = useCurrentFrame();

  // 扫描路径点
  const scanPath = [
    { x: 400, y: 300 },
    { x: 800, y: 350 },
    { x: 1200, y: 400 },
    { x: 1400, y: 600 },
    { x: 1000, y: 700 },
    { x: 600, y: 650 },
  ];

  // 当前扫描进度
  const progress = interpolate(frame, [0, 90], [0, scanPath.length], {
    extrapolateRight: 'clamp',
  });

  // 文字淡入
  const textOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: bg_color }}>
      <svg
        width="1920"
        height="1080"
        viewBox="0 0 1920 1080"
        style={{ position: 'absolute' }}
      >
        {/* 噪点纹理 */}
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

        <rect width="1920" height="1080" filter="url(#noise)" />

        {/* 扫描路径线条 */}
        {scanPath.map((point, index) => {
          if (index === 0 || progress < index) return null;
          const prevPoint = scanPath[index - 1];
          const lineProgress = Math.min(1, Math.max(0, progress - index));

          return (
            <line
              key={index}
              x1={prevPoint.x}
              y1={prevPoint.y}
              x2={prevPoint.x + (point.x - prevPoint.x) * lineProgress}
              y2={prevPoint.y + (point.y - prevPoint.y) * lineProgress}
              stroke={accent_color}
              strokeWidth="3"
              opacity="0.8"
            />
          );
        })}

        {/* 扫描焦点圆圈 */}
        {scanPath.map((point, index) => {
          if (progress < index) return null;
          const pointOpacity = progress > index + 1 ? 0.4 : 1;
          const scale = progress > index + 1 ? 0.8 : 1;

          return (
            <g key={`point-${index}`}>
              {/* 外圈脉冲 */}
              <circle
                cx={point.x}
                cy={point.y}
                r={30 * scale}
                fill="none"
                stroke={accent_color}
                strokeWidth="2"
                opacity={pointOpacity * 0.5}
              />
              {/* 内圈实心 */}
              <circle
                cx={point.x}
                cy={point.y}
                r={15 * scale}
                fill={accent_color}
                opacity={pointOpacity}
              />
              {/* 焦点编号 */}
              <text
                x={point.x}
                y={point.y + 6}
                textAnchor="middle"
                fill={bg_color}
                fontSize="18"
                fontWeight="bold"
              >
                {index + 1}
              </text>
            </g>
          );
        })}

        {/* 当前扫描位置的高亮圆圈 */}
        {progress > 0 && progress < scanPath.length && (
          <circle
            cx={scanPath[Math.floor(progress)].x}
            cy={scanPath[Math.floor(progress)].y}
            r={40}
            fill="none"
            stroke={accent_color}
            strokeWidth="3"
            opacity={interpolate(frame % 15, [0, 15], [0.3, 1], {
              extrapolateRight: 'clamp',
            })}
          />
        )}
      </svg>

      {/* 标题文字 */}
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
