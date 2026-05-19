import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

interface VisualGuideProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function VisualGuide({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '视觉引导三要素',
  text_sub = '留白 · 线条 · 光影',
}: VisualGuideProps) {
  const frame = useCurrentFrame();

  // 三个要素依次出现
  const element1Opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const element2Opacity = interpolate(frame, [40, 70], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const element3Opacity = interpolate(frame, [80, 110], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 文字淡入
  const textOpacity = interpolate(frame, [120, 150], [0, 1], {
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
          {/* 光影渐变 */}
          <radialGradient id="lightGradient">
            <stop offset="0%" stopColor={accent_color} stopOpacity="0.8" />
            <stop offset="100%" stopColor={accent_color} stopOpacity="0" />
          </radialGradient>
        </defs>

        <rect width="1920" height="1080" filter="url(#noise)" />

        {/* 第一部分：留白 - 左侧大面积空白 */}
        <g opacity={element1Opacity}>
          {/* 右侧内容区域 */}
          <rect
            x="1200"
            y="300"
            width="500"
            height="400"
            fill={text_color}
            opacity="0.1"
          />
          {/* 留白标注 */}
          <text
            x="600"
            y="400"
            textAnchor="middle"
            fill={accent_color}
            fontSize="48"
            fontWeight="bold"
          >
            留白
          </text>
          {/* 箭头指向留白区域 */}
          <path
            d="M 800 400 L 1100 400"
            stroke={accent_color}
            strokeWidth="3"
            fill="none"
            markerEnd="url(#arrowhead)"
          />
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill={accent_color} />
            </marker>
          </defs>
        </g>

        {/* 第二部分：线条 - 引导视线的线条 */}
        <g opacity={element2Opacity}>
          {/* S型引导线 */}
          <path
            d="M 300 600 Q 600 750, 900 650 T 1500 800"
            stroke={accent_color}
            strokeWidth="4"
            fill="none"
          />
          {/* 线条标注 */}
          <text
            x="1200"
            y="600"
            textAnchor="middle"
            fill={accent_color}
            fontSize="48"
            fontWeight="bold"
          >
            线条
          </text>
          {/* 视线跟随点 */}
          {[0, 0.25, 0.5, 0.75, 1].map((t, i) => {
            const x = 300 + t * 1200;
            const y = 600 + Math.sin(t * Math.PI * 2) * 75 + 100;
            return (
              <circle
                key={i}
                cx={x}
                cy={y}
                r="8"
                fill={accent_color}
                opacity={0.6}
              />
            );
          })}
        </g>

        {/* 第三部分：光影 - 光线照射效果 */}
        <g opacity={element3Opacity}>
          {/* 光源 */}
          <circle cx="1400" cy="350" r="80" fill="url(#lightGradient)" />
          {/* 光线扩散 */}
          {[0, 30, 60, 90, 120].map((angle) => {
            const rad = ((angle + 120) * Math.PI) / 180;
            const x2 = 1400 + Math.cos(rad) * 400;
            const y2 = 350 + Math.sin(rad) * 400;
            return (
              <line
                key={angle}
                x1="1400"
                y1="350"
                x2={x2}
                y2={y2}
                stroke={accent_color}
                strokeWidth="2"
                opacity="0.3"
              />
            );
          })}
          {/* 光影标注 */}
          <text
            x="1400"
            y="250"
            textAnchor="middle"
            fill={accent_color}
            fontSize="48"
            fontWeight="bold"
          >
            光影
          </text>
        </g>
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
