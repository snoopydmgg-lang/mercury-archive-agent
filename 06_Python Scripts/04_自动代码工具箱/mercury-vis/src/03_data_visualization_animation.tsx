import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

export const DataVisualizationAnimation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const initialNumberScale = spring({ frame: frame - 0, fps, config: { damping: 10 } });
  const arrowProgress = interpolate(frame, [fps * 1, fps * 3], [0, 1], { extrapolateRight: 'clamp' });
  const finalNumberScale = spring({ frame: frame - fps * 3, fps, config: { damping: 10 } });
  const progressBar1 = interpolate(frame, [fps * 4, fps * 5], [0, 0.03], { extrapolateRight: 'clamp' });
  const progressBar2 = interpolate(frame, [fps * 4.5, fps * 5.5], [0, 0.08], { extrapolateRight: 'clamp' });
  const comparisonTextOpacity = interpolate(frame, [fps * 6, fps * 7], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ backgroundColor: '#F5F4F0' }}>
      <div style={{ position: 'absolute', top: '10%', left: '50%', transform: 'translateX(-50%)', fontSize: 36, fontWeight: 700, color: '#2D2B2A' }}>
        朋友圈点赞率对比
      </div>

      <div style={{ position: 'absolute', top: '35%', left: '25%', transform: `translate(-50%, -50%) scale(${initialNumberScale})` }}>
        <div style={{ fontSize: 120, fontWeight: 900, color: '#2D2B2A' }}>3%</div>
        <div style={{ fontSize: 24, color: '#2D2B2A', textAlign: 'center', marginTop: 10 }}>居中构图</div>
      </div>

      <svg width="100%" height="100%" viewBox="0 0 1080 1920" style={{ position: 'absolute', top: 0, left: 0 }}>
        <path d={`M 350 672 L ${350 + 380 * arrowProgress} 672`} stroke="#D36B4D" strokeWidth="8" fill="none" />
        {arrowProgress > 0.9 && <path d="M 730 672 L 700 652 L 700 692 Z" fill="#D36B4D" />}
        <text x="540" y="640" fontSize="28" fill="#D36B4D" fontWeight="700" textAnchor="middle" opacity={arrowProgress}>+167%</text>
      </svg>

      <div style={{ position: 'absolute', top: '35%', right: '25%', transform: `translate(50%, -50%) scale(${finalNumberScale})` }}>
        <div style={{ fontSize: 120, fontWeight: 900, color: '#D36B4D' }}>8%</div>
        <div style={{ fontSize: 24, color: '#2D2B2A', textAlign: 'center', marginTop: 10 }}>三分法构图</div>
      </div>

      <div style={{ position: 'absolute', bottom: '12%', left: '50%', transform: 'translateX(-50%)', opacity: comparisonTextOpacity, textAlign: 'center' }}>
        <div style={{ fontSize: 32, fontWeight: 700, color: '#2D2B2A' }}>同样的照片 只是改变了构图方式</div>
      </div>
    </AbsoluteFill>
  );
};
