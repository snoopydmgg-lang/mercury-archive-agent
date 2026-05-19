import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

interface ElementAttractionProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function ElementAttraction({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '视觉吸引力',
  text_sub = '元素对比 · 焦点突出',
}: ElementAttractionProps) {
  const frame = useCurrentFrame();

  // 普通元素淡入
  const normalOpacity = interpolate(frame, [0, 30], [0, 0.3], {
    extrapolateRight: 'clamp',
  });

  // 突出元素放大
  const highlightScale = interpolate(frame, [30, 60], [1, 1.5], {
    extrapolateRight: 'clamp',
  });

  // 突出元素脉冲
  const pulseScale =
    1 + Math.sin((frame - 60) * 0.2) * 0.1 * (frame > 60 ? 1 : 0);

  // 文字淡入
  const textOpacity = interpolate(frame, [90, 120], [0, 1], {
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

        {/* 普通元素网格 */}
        {Array.from({ length: 5 }).map((_, row) =>
          Array.from({ length: 8 }).map((_, col) => {
            const x = 400 + col * 150;
            const y = 300 + row * 120;
            const isCenterElement = row === 2 && col === 4;

            if (isCenterElement) return null; // 中心元素单独处理

            return (
              <circle
                key={`${row}-${col}`}
                cx={x}
                cy={y}
                r="30"
                fill={text_color}
                opacity={normalOpacity}
              />
            );
          })
        )}

        {/* 突出的中心元素 */}
        <g transform={`translate(960, 540)`}>
          <circle
            cx="0"
            cy="0"
            r={50 * highlightScale * pulseScale}
            fill={accent_color}
            opacity="0.9"
          />
          {/* 外圈光晕 */}
          {frame > 60 && (
            <>
              <circle
                cx="0"
                cy="0"
                r={80 * pulseScale}
                fill="none"
                stroke={accent_color}
                strokeWidth="3"
                opacity="0.5"
              />
              <circle
                cx="0"
                cy="0"
                r={110 * pulseScale}
                fill="none"
                stroke={accent_color}
                strokeWidth="2"
                opacity="0.3"
              />
            </>
          )}
        </g>

        {/* 对比标注线 */}
        {frame > 60 && (
          <>
            {/* 左侧标注 */}
            <line
              x1="250"
              y1="540"
              x2="800"
              y2="540"
              stroke={text_color}
              strokeWidth="2"
              strokeDasharray="5,5"
              opacity="0.5"
            />
            <text
              x="200"
              y="550"
              textAnchor="end"
              fill={text_color}
              fontSize="28"
              opacity="0.7"
            >
              普通元素
            </text>

            {/* 右侧标注 */}
            <line
              x1="1120"
              y1="540"
              x2="1670"
              y2="540"
              stroke={accent_color}
              strokeWidth="2"
              strokeDasharray="5,5"
              opacity="0.5"
            />
            <text
              x="1720"
              y="550"
              textAnchor="start"
              fill={accent_color}
              fontSize="28"
              fontWeight="bold"
            >
              视觉焦点
            </text>
          </>
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
