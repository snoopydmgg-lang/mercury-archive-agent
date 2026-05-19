import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

interface LightbulbMomentProps {
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  text_main?: string;
  text_sub?: string;
}

export function LightbulbMoment({
  bg_color = '#F5F4F0',
  text_color = '#2D2B2A',
  accent_color = '#D36B4D',
  text_main = '顿悟时刻',
  text_sub = '灵感闪现 · 认知突破',
}: LightbulbMomentProps) {
  const frame = useCurrentFrame();

  // 灯泡轮廓绘制
  const bulbProgress = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 灯泡点亮
  const lightIntensity = interpolate(frame, [30, 45], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 光芒扩散
  const raysProgress = interpolate(frame, [45, 75], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // 脉冲效果
  const pulse = frame > 45 ? 1 + Math.sin((frame - 45) * 0.3) * 0.15 : 1;

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
          {/* 光晕渐变 */}
          <radialGradient id="glowGradient">
            <stop offset="0%" stopColor={accent_color} stopOpacity="0.9" />
            <stop offset="50%" stopColor={accent_color} stopOpacity="0.4" />
            <stop offset="100%" stopColor={accent_color} stopOpacity="0" />
          </radialGradient>
        </defs>

        <rect width="1920" height="1080" filter="url(#noise)" />

        <g transform="translate(960, 540)">
          {/* 灯泡玻璃部分 */}
          <ellipse
            cx="0"
            cy="-50"
            rx={80 * bulbProgress}
            ry={100 * bulbProgress}
            fill="none"
            stroke={text_color}
            strokeWidth="4"
          />

          {/* 灯泡底座 */}
          {bulbProgress >= 1 && (
            <>
              <rect
                x="-40"
                y="50"
                width="80"
                height="30"
                fill="none"
                stroke={text_color}
                strokeWidth="4"
              />
              <line
                x1="-40"
                y1="60"
                x2="40"
                y2="60"
                stroke={text_color}
                strokeWidth="2"
              />
              <line
                x1="-40"
                y1="70"
                x2="40"
                y2="70"
                stroke={text_color}
                strokeWidth="2"
              />
            </>
          )}

          {/* 灯泡内部光芒 */}
          {lightIntensity > 0 && (
            <>
              {/* 中心光源 */}
              <circle
                cx="0"
                cy="-50"
                r={50 * lightIntensity * pulse}
                fill="url(#glowGradient)"
              />
              {/* 灯丝 */}
              <path
                d="M -20,-50 Q 0,-30, 20,-50"
                stroke={accent_color}
                strokeWidth="3"
                fill="none"
                opacity={lightIntensity}
              />
            </>
          )}

          {/* 外部光芒射线 */}
          {raysProgress > 0 &&
            [0, 45, 90, 135, 180, 225, 270, 315].map((angle) => {
              const rad = (angle * Math.PI) / 180;
              const startR = 120;
              const endR = 120 + 100 * raysProgress;
              const x1 = Math.cos(rad) * startR;
              const y1 = Math.sin(rad) * startR - 50;
              const x2 = Math.cos(rad) * endR * pulse;
              const y2 = Math.sin(rad) * endR * pulse - 50;

              return (
                <line
                  key={angle}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={accent_color}
                  strokeWidth="4"
                  strokeLinecap="round"
                  opacity={raysProgress * 0.8}
                />
              );
            })}

          {/* 闪光星星 */}
          {raysProgress > 0.5 &&
            [
              { x: -150, y: -180 },
              { x: 150, y: -180 },
              { x: -180, y: 0 },
              { x: 180, y: 0 },
            ].map((pos, i) => (
              <g key={i} opacity={interpolate(frame, [60, 75], [0, 1])}>
                <line
                  x1={pos.x - 15}
                  y1={pos.y}
                  x2={pos.x + 15}
                  y2={pos.y}
                  stroke={accent_color}
                  strokeWidth="3"
                />
                <line
                  x1={pos.x}
                  y1={pos.y - 15}
                  x2={pos.x}
                  y2={pos.y + 15}
                  stroke={accent_color}
                  strokeWidth="3"
                />
              </g>
            ))}
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

      {/* 底部说明 */}
      <div
        style={{
          position: 'absolute',
          bottom: '100px',
          left: '0',
          right: '0',
          textAlign: 'center',
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
          从技巧到审美的转变
        </p>
      </div>
    </AbsoluteFill>
  );
}
