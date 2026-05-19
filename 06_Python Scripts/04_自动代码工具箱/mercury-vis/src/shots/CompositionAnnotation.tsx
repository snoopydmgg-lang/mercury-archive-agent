import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

interface CompositionAnnotationProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function CompositionAnnotation({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '构图标注',
  text_sub = '手绘线条 · 结构解析',
}: CompositionAnnotationProps) {
  const frame = useCurrentFrame();

  // 矩形框架绘制进度
  const frameProgress = interpolate(frame, [0, 40], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 三分线绘制进度
  const gridProgress = interpolate(frame, [40, 70], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 标注点出现
  const annotationOpacity = interpolate(frame, [70, 90], [0, 1], {
    extrapolateRight: 'clamp',
  });

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

        {/* 主框架矩形 - 手绘风格 */}
        <rect
          x="400"
          y="250"
          width={1120 * frameProgress}
          height={580 * frameProgress}
          fill="none"
          stroke={text_color}
          strokeWidth="4"
          strokeLinecap="round"
        />

        {/* 三分法网格线 - 竖线 */}
        {frameProgress >= 1 && (
          <>
            <line
              x1="773"
              y1="250"
              x2="773"
              y2={250 + 580 * gridProgress}
              stroke={accent_color}
              strokeWidth="2"
              strokeDasharray="10,5"
            />
            <line
              x1="1147"
              y1="250"
              x2="1147"
              y2={250 + 580 * gridProgress}
              stroke={accent_color}
              strokeWidth="2"
              strokeDasharray="10,5"
            />
          </>
        )}

        {/* 三分法网格线 - 横线 */}
        {frameProgress >= 1 && (
          <>
            <line
              x1="400"
              y1="443"
              x2={400 + 1120 * gridProgress}
              y2="443"
              stroke={accent_color}
              strokeWidth="2"
              strokeDasharray="10,5"
            />
            <line
              x1="400"
              y1="637"
              x2={400 + 1120 * gridProgress}
              y2="637"
              stroke={accent_color}
              strokeWidth="2"
              strokeDasharray="10,5"
            />
          </>
        )}

        {/* 黄金交叉点标注 */}
        {gridProgress >= 1 && (
          <>
            {/* 左上交叉点 */}
            <g opacity={annotationOpacity}>
              <circle cx="773" cy="443" r="15" fill={accent_color} />
              <circle
                cx="773"
                cy="443"
                r="25"
                fill="none"
                stroke={accent_color}
                strokeWidth="2"
              />
              <text
                x="773"
                y="410"
                textAnchor="middle"
                fill={accent_color}
                fontSize="24"
                fontWeight="bold"
              >
                焦点1
              </text>
            </g>

            {/* 右上交叉点 */}
            <g opacity={annotationOpacity}>
              <circle cx="1147" cy="443" r="15" fill={accent_color} />
              <circle
                cx="1147"
                cy="443"
                r="25"
                fill="none"
                stroke={accent_color}
                strokeWidth="2"
              />
              <text
                x="1147"
                y="410"
                textAnchor="middle"
                fill={accent_color}
                fontSize="24"
                fontWeight="bold"
              >
                焦点2
              </text>
            </g>

            {/* 左下交叉点 */}
            <g opacity={annotationOpacity}>
              <circle cx="773" cy="637" r="15" fill={accent_color} />
              <circle
                cx="773"
                cy="637"
                r="25"
                fill="none"
                stroke={accent_color}
                strokeWidth="2"
              />
            </g>

            {/* 右下交叉点 */}
            <g opacity={annotationOpacity}>
              <circle cx="1147" cy="637" r="15" fill={accent_color} />
              <circle
                cx="1147"
                cy="637"
                r="25"
                fill="none"
                stroke={accent_color}
                strokeWidth="2"
              />
            </g>
          </>
        )}

        {/* 手绘箭头标注 */}
        {annotationOpacity > 0 && (
          <>
            {/* 指向焦点1的箭头 */}
            <path
              d="M 650 350 Q 700 380, 750 420"
              stroke={accent_color}
              strokeWidth="3"
              fill="none"
              opacity={annotationOpacity}
            />
            <polygon
              points="750,420 745,410 755,415"
              fill={accent_color}
              opacity={annotationOpacity}
            />
            <text
              x="600"
              y="350"
              fill={text_color}
              fontSize="28"
              opacity={annotationOpacity * 0.8}
            >
              视觉重心
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
