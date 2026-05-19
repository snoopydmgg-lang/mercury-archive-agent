import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

interface FourElementsProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function FourElements({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '摄影四要素',
  text_sub = '主体 · 留白 · 光影 · 情感',
}: FourElementsProps) {
  const frame = useCurrentFrame();

  // 中心圆出现
  const centerOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 四个要素依次出现
  const element1 = interpolate(frame, [20, 40], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const element2 = interpolate(frame, [40, 60], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const element3 = interpolate(frame, [60, 80], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const element4 = interpolate(frame, [80, 100], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 连接线出现
  const linesOpacity = interpolate(frame, [100, 120], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 文字淡入
  const textOpacity = interpolate(frame, [120, 150], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const elements = [
    { label: '主体', angle: -90, opacity: element1, desc: 'Subject' },
    { label: '留白', angle: 0, opacity: element2, desc: 'Space' },
    { label: '光影', angle: 90, opacity: element3, desc: 'Light' },
    { label: '情感', angle: 180, opacity: element4, desc: 'Emotion' },
  ];

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

        <g transform="translate(960, 540)">
          {/* 中心圆 */}
          <circle
            cx="0"
            cy="0"
            r="80"
            fill={accent_color}
            opacity={centerOpacity * 0.2}
          />
          <circle
            cx="0"
            cy="0"
            r="80"
            fill="none"
            stroke={accent_color}
            strokeWidth="4"
            opacity={centerOpacity}
          />
          <text
            x="0"
            y="10"
            textAnchor="middle"
            fill={accent_color}
            fontSize="36"
            fontWeight="bold"
            opacity={centerOpacity}
          >
            构图
          </text>

          {/* 四个要素圆圈 */}
          {elements.map((element, index) => {
            const rad = (element.angle * Math.PI) / 180;
            const distance = 280;
            const x = Math.cos(rad) * distance;
            const y = Math.sin(rad) * distance;

            return (
              <g key={index} opacity={element.opacity}>
                {/* 连接线 */}
                <line
                  x1="0"
                  y1="0"
                  x2={x}
                  y2={y}
                  stroke={text_color}
                  strokeWidth="2"
                  strokeDasharray="5,5"
                  opacity={linesOpacity * 0.5}
                />

                {/* 要素圆圈 */}
                <circle
                  cx={x}
                  cy={y}
                  r="100"
                  fill={bg_color}
                  stroke={text_color}
                  strokeWidth="3"
                />

                {/* 要素标签 */}
                <text
                  x={x}
                  y={y - 10}
                  textAnchor="middle"
                  fill={text_color}
                  fontSize="42"
                  fontWeight="bold"
                >
                  {element.label}
                </text>

                {/* 英文副标题 */}
                <text
                  x={x}
                  y={y + 25}
                  textAnchor="middle"
                  fill={accent_color}
                  fontSize="24"
                >
                  {element.desc}
                </text>

                {/* 编号 */}
                <circle
                  cx={x}
                  cy={y - 70}
                  r="18"
                  fill={accent_color}
                  opacity="0.8"
                />
                <text
                  x={x}
                  y={y - 64}
                  textAnchor="middle"
                  fill={bg_color}
                  fontSize="20"
                  fontWeight="bold"
                >
                  {index + 1}
                </text>
              </g>
            );
          })}

          {/* 外圈装饰圆 */}
          {linesOpacity > 0 && (
            <>
              <circle
                cx="0"
                cy="0"
                r="420"
                fill="none"
                stroke={text_color}
                strokeWidth="1"
                opacity={linesOpacity * 0.3}
              />
              <circle
                cx="0"
                cy="0"
                r="450"
                fill="none"
                stroke={text_color}
                strokeWidth="1"
                opacity={linesOpacity * 0.2}
              />
            </>
          )}
        </g>
      </svg>

      {/* 标题文字 - 移到左侧 */}
      <div
        style={{
          position: 'absolute',
          top: '80px',
          left: '80px',
          opacity: textOpacity,
        }}
      >
        <h1
          style={{
            fontFamily:
              "'Source Han Serif SC', 'Noto Serif CJK SC', 'Microsoft YaHei', Georgia, serif",
            fontSize: '64px',
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
            fontSize: '32px',
            color: accent_color,
            margin: '15px 0 0 0',
            letterSpacing: '2px',
          }}
        >
          {text_sub}
        </p>
      </div>

      {/* 底部说明 */}
      <div
        style={{
          position: 'absolute',
          bottom: '50px',
          left: '80px',
          opacity: textOpacity,
        }}
      >
        <p
          style={{
            fontFamily: "'Microsoft YaHei', '微软雅黑', Inter, sans-serif",
            fontSize: '28px',
            color: text_color,
            opacity: 0.7,
            margin: 0,
          }}
        >
          好照片的核心框架
        </p>
      </div>
    </AbsoluteFill>
  );
}
