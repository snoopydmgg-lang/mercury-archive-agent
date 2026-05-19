import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

export const FourElementsAnimation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const centerScale = spring({ frame: frame - 0, fps, config: { damping: 12 } });
  const element1Scale = spring({ frame: frame - fps * 1, fps, config: { damping: 10 } });
  const element2Scale = spring({ frame: frame - fps * 2, fps, config: { damping: 10 } });
  const element3Scale = spring({ frame: frame - fps * 3, fps, config: { damping: 10 } });
  const element4Scale = spring({ frame: frame - fps * 4, fps, config: { damping: 10 } });
  const connectionProgress = interpolate(frame, [fps * 5, fps * 7], [0, 1], { extrapolateRight: 'clamp' });
  const emphasisPulse = Math.sin((frame - fps * 7) / 10) * 0.5 + 0.5;

  const elements = [
    { label: '技术', icon: '⚙️', color: '#2D2B2A', angle: 0 },
    { label: '构图', icon: '📐', color: '#2D2B2A', angle: Math.PI / 2 },
    { label: '光影', icon: '💡', color: '#2D2B2A', angle: Math.PI },
    { label: '情感', icon: '❤️', color: '#D36B4D', angle: (Math.PI * 3) / 2 },
  ];

  const scales = [element1Scale, element2Scale, element3Scale, element4Scale];

  return (
    <AbsoluteFill style={{ backgroundColor: '#F5F4F0' }}>
      <div style={{ position: 'absolute', top: '8%', left: '50%', transform: 'translateX(-50%)', fontSize: 40, fontWeight: 700, color: '#2D2B2A', textAlign: 'center' }}>
        好照片的四要素
      </div>

      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: `translate(-50%, -50%) scale(${centerScale})` }}>
        <div style={{ width: 180, height: 180, borderRadius: '50%', backgroundColor: '#D36B4D', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 8px 32px rgba(211, 107, 77, 0.3)' }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#F5F4F0', textAlign: 'center' }}>好照片</div>
        </div>
      </div>

      <svg width="100%" height="100%" viewBox="0 0 1080 1920" style={{ position: 'absolute', top: 0, left: 0 }}>
        {elements.map((element, i) => {
          const centerX = 540;
          const centerY = 960;
          const radius = 300;
          const x = centerX + Math.cos(element.angle) * radius;
          const y = centerY + Math.sin(element.angle) * radius;
          return (
            <line key={i} x1={centerX} y1={centerY} x2={centerX + (x - centerX) * connectionProgress} y2={centerY + (y - centerY) * connectionProgress} stroke={element.color} strokeWidth="3" strokeDasharray="8,4" opacity={0.6} />
          );
        })}
      </svg>

      {elements.map((element, i) => {
        const centerX = 540;
        const centerY = 960;
        const radius = 300;
        const x = centerX + Math.cos(element.angle) * radius;
        const y = centerY + Math.sin(element.angle) * radius;
        const isEmphasis = i === 3 && frame > fps * 7;
        const scale = scales[i] * (isEmphasis ? 1 + emphasisPulse * 0.1 : 1);

        return (
          <div key={i} style={{ position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) scale(${scale})` }}>
            <div style={{ width: 140, height: 140, borderRadius: '50%', backgroundColor: '#F5F4F0', border: `4px solid ${element.color}`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ fontSize: 48, marginBottom: 8 }}>{element.icon}</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: element.color }}>{element.label}</div>
            </div>
          </div>
        );
      })}

      <div style={{ position: 'absolute', bottom: '12%', left: '50%', transform: 'translateX(-50%)', opacity: interpolate(frame, [fps * 7, fps * 8], [0, 1], { extrapolateRight: 'clamp' }), textAlign: 'center' }}>
        <div style={{ fontSize: 36, fontWeight: 700, color: '#D36B4D' }}>情感共鸣最关键</div>
        <div style={{ fontSize: 24, color: '#2D2B2A', marginTop: 10 }}>技术永远是为情感服务的</div>
      </div>
    </AbsoluteFill>
  );
};
