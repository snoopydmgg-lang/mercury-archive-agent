import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

export const CommentArrowAnimation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const textOpacity = interpolate(frame, [0, fps * 1], [0, 1], { extrapolateRight: 'clamp' });
  const arrowProgress = interpolate(frame, [fps * 1, fps * 3], [0, 1], { extrapolateRight: 'clamp' });
  const bounceOffset = frame > fps * 3 ? Math.sin((frame - fps * 3) / 15) * 20 : 0;
  const commentIconPulse = frame > fps * 3 ? Math.sin((frame - fps * 3) / 20) * 0.3 + 0.7 : 1;
  const fingerScale = frame > fps * 4 ? 1 - Math.max(0, Math.sin((frame - fps * 4) / 10)) * 0.2 : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: '#F5F4F0' }}>
      <div style={{ position: 'absolute', top: '25%', left: '50%', transform: 'translateX(-50%)', opacity: textOpacity, textAlign: 'center' }}>
        <div style={{ fontSize: 48, fontWeight: 700, color: '#2D2B2A', marginBottom: 20 }}>
          想从"模仿"升级到"创造"？
        </div>
        <div style={{ fontSize: 36, fontWeight: 600, color: '#D36B4D' }}>
          评论区有链接 👇
        </div>
      </div>

      <svg width="100%" height="100%" viewBox="0 0 1080 1920" style={{ position: 'absolute', top: 0, left: 0 }}>
        <path d={`M 540 600 Q 540 ${600 + 200 * arrowProgress}, ${540 + 150 * arrowProgress} ${600 + 400 * arrowProgress} T 540 ${600 + 800 * arrowProgress}`} stroke="#D36B4D" strokeWidth="8" fill="none" strokeLinecap="round" />
        {arrowProgress > 0.95 && <path d={`M 540 ${1400 + bounceOffset} L 520 ${1370 + bounceOffset} L 560 ${1370 + bounceOffset} Z`} fill="#D36B4D" />}
      </svg>

      <div style={{ position: 'absolute', bottom: '20%', left: '50%', transform: `translate(-50%, ${bounceOffset}px) scale(${commentIconPulse})` }}>
        <div style={{ width: 200, height: 200, borderRadius: '50%', backgroundColor: '#D36B4D', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 8px 32px rgba(211, 107, 77, ${0.3 * commentIconPulse})` }}>
          <svg width="100" height="100" viewBox="0 0 100 100">
            <path d="M 20 30 L 80 30 L 80 60 L 55 60 L 50 70 L 45 60 L 20 60 Z" fill="#F5F4F0" stroke="#F5F4F0" strokeWidth="2" />
            <circle cx="35" cy="45" r="4" fill="#D36B4D" />
            <circle cx="50" cy="45" r="4" fill="#D36B4D" />
            <circle cx="65" cy="45" r="4" fill="#D36B4D" />
          </svg>
        </div>
      </div>

      {frame > fps * 4 && (
        <div style={{ position: 'absolute', bottom: '18%', left: '58%', transform: `scale(${fingerScale})`, fontSize: 60 }}>
          👆
        </div>
      )}

      <div style={{ position: 'absolute', bottom: '10%', left: '50%', transform: 'translateX(-50%)', opacity: frame > fps * 3 ? Math.sin((frame - fps * 3) / 20) * 0.5 + 0.5 : 0 }}>
        <div style={{ fontSize: 32, fontWeight: 700, color: '#D36B4D', textAlign: 'center' }}>
          点击评论区
        </div>
      </div>
    </AbsoluteFill>
  );
};
