import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

interface GoldenRatioProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function GoldenRatio({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '黄金分割',
  text_sub = '1.618 · 美学比例',
}: GoldenRatioProps) {
  const frame = useCurrentFrame();

  // 矩形绘制
  const rectProgress = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 黄金分割线浮现
  const lineProgress = interpolate(frame, [30, 60], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 螺旋线绘制
  const spiralProgress = interpolate(frame, [60, 90], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 文字淡入
  const textOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 黄金比例 φ = 1.618
  const phi = 1.618;
  const totalWidth = 800;
  const totalHeight = totalWidth / phi;

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

        {/* 主矩形 */}
        <rect
          x="560"
          y="290"
          width={totalWidth * rectProgress}
          height={totalHeight * rectProgress}
          fill="none"
          stroke={text_color}
          strokeWidth="4"
        />

        {/* 黄金分割竖线 */}
        {rectProgress >= 1 && (
          <line
            x1={560 + totalWidth / phi}
            y1="290"
            x2={560 + totalWidth / phi}
            y2={290 + totalHeight * lineProgress}
            stroke={accent_color}
            strokeWidth="3"
          />
        )}

        {/* 黄金分割横线 */}
        {rectProgress >= 1 && (
          <line
            x1="560"
            y1={290 + totalHeight / phi}
            x2={560 + totalWidth * lineProgress}
            y2={290 + totalHeight / phi}
            stroke={accent_color}
            strokeWidth="3"
          />
        )}

        {/* 黄金螺旋线 */}
        {lineProgress >= 1 && spiralProgress > 0 && (
          <path
            d={generateGoldenSpiral(560, 290, totalWidth, spiralProgress)}
            fill="none"
            stroke={accent_color}
            strokeWidth="3"
            opacity="0.8"
          />
        )}

        {/* 比例标注 */}
        {lineProgress >= 1 && (
          <>
            {/* 长边标注 */}
            <g opacity={textOpacity}>
              <line
                x1="560"
                y1={290 + totalHeight + 40}
                x2={560 + totalWidth / phi}
                y2={290 + totalHeight + 40}
                stroke={accent_color}
                strokeWidth="2"
              />
              <text
                x={560 + totalWidth / phi / 2}
                y={290 + totalHeight + 70}
                textAnchor="middle"
                fill={accent_color}
                fontSize="28"
                fontWeight="bold"
              >
                φ
              </text>
            </g>

            {/* 短边标注 */}
            <g opacity={textOpacity}>
              <line
                x1={560 + totalWidth / phi}
                y1={290 + totalHeight + 40}
                x2={560 + totalWidth}
                y2={290 + totalHeight + 40}
                stroke={text_color}
                strokeWidth="2"
              />
              <text
                x={560 + totalWidth / phi + (totalWidth - totalWidth / phi) / 2}
                y={290 + totalHeight + 70}
                textAnchor="middle"
                fill={text_color}
                fontSize="28"
              >
                1
              </text>
            </g>

            {/* 比例公式 */}
            <text
              x="960"
              y="850"
              textAnchor="middle"
              fill={accent_color}
              fontSize="48"
              fontWeight="bold"
              opacity={textOpacity}
            >
              φ = 1.618...
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

// 生成黄金螺旋路径
function generateGoldenSpiral(
  startX: number,
  startY: number,
  size: number,
  progress: number
): string {
  const phi = 1.618;
  let path = `M ${startX + size / phi} ${startY}`;

  let currentSize = size;
  let x = startX;
  let y = startY;
  const segments = Math.floor(progress * 4); // 最多4个象限

  for (let i = 0; i < segments; i++) {
    const nextSize = currentSize / phi;
    switch (i % 4) {
      case 0: // 右上
        path += ` Q ${x + currentSize} ${y}, ${x + currentSize} ${y + nextSize}`;
        x = x + currentSize - nextSize;
        break;
      case 1: // 左上
        path += ` Q ${x + nextSize} ${y}, ${x} ${y + nextSize}`;
        y = y + nextSize;
        break;
      case 2: // 左下
        path += ` Q ${x} ${y + nextSize}, ${x + nextSize} ${y + nextSize}`;
        break;
      case 3: // 右下
        path += ` Q ${x + nextSize} ${y}, ${x + nextSize} ${y}`;
        break;
    }
    currentSize = nextSize;
  }

  return path;
}
