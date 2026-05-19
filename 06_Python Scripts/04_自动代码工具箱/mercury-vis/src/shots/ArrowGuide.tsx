import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

interface ArrowGuideProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function ArrowGuide({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '视线引导',
  text_sub = '箭头指向 · 方向感',
}: ArrowGuideProps) {
  const frame = useCurrentFrame();

  // 箭头生长动画
  const arrowProgress = interpolate(frame, [0, 60], [0, 1], {
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
          {/* 箭头标记 */}
          <marker
            id="arrowhead-main"
            markerWidth="20"
            markerHeight="20"
            refX="18"
            refY="10"
            orient="auto"
          >
            <polygon points="0 0, 20 10, 0 20" fill={accent_color} />
          </marker>
        </defs>

        <rect width="1920" height="1080" filter="url(#noise)" />

        {/* 中心主箭头 - 向右 */}
        <line
          x1="400"
          y1="540"
          x2={400 + 800 * arrowProgress}
          y2="540"
          stroke={accent_color}
          strokeWidth="8"
          markerEnd="url(#arrowhead-main)"
        />

        {/* 分支箭头 - 向上 */}
        {arrowProgress > 0.5 && (
          <line
            x1="960"
            y1="540"
            x2="960"
            y2={540 - 300 * (arrowProgress - 0.5) * 2}
            stroke={accent_color}
            strokeWidth="6"
            markerEnd="url(#arrowhead-main)"
            opacity="0.8"
          />
        )}

        {/* 分支箭头 - 向下 */}
        {arrowProgress > 0.5 && (
          <line
            x1="960"
            y1="540"
            x2="960"
            y2={540 + 300 * (arrowProgress - 0.5) * 2}
            stroke={accent_color}
            strokeWidth="6"
            markerEnd="url(#arrowhead-main)"
            opacity="0.8"
          />
        )}

        {/* 起点圆圈 */}
        <circle cx="400" cy="540" r="20" fill={accent_color} />

        {/* 终点圆圈 */}
        {arrowProgress > 0.8 && (
          <>
            <circle
              cx="1200"
              cy="540"
              r="30"
              fill="none"
              stroke={accent_color}
              strokeWidth="4"
            />
            <circle cx="1200" cy="540" r="15" fill={accent_color} />
          </>
        )}

        {/* 视线路径标注 */}
        {arrowProgress > 0.3 && (
          <text
            x="700"
            y="480"
            textAnchor="middle"
            fill={text_color}
            fontSize="32"
            opacity="0.6"
          >
            视线路径
          </text>
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
