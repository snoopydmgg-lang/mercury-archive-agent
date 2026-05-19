import React from 'react';
import {
  useCurrentFrame,
  interpolate,
  AbsoluteFill,
  Img,
  Video,
  staticFile,
} from 'remotion';

const FONT = '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif';

export function ImageShowcase({
  asset_path,
  caption,
  asset_type = 'image',
  ken_burns_direction = 'in',
  duration_sec = 5,
  fallback_color = '#2D2B2A',
}: {
  asset_path?: string;
  caption?: string;
  asset_type?: 'image' | 'video';
  ken_burns_direction?: 'in' | 'out';
  duration_sec?: number;
  fallback_color?: string;
}) {
  const frame = useCurrentFrame();
  const fps = 30;
  const totalFrames = duration_sec * fps;

  // Ken Burns effect
  const scale = interpolate(
    frame,
    [0, totalFrames],
    ken_burns_direction === 'in' ? [1, 1.15] : [1.15, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Caption fade in
  const captionProgress = interpolate(
    frame,
    [Math.floor(totalFrames * 0.6), Math.floor(totalFrames * 0.8)],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Resolve asset path - use staticFile() for local files
  const resolvedSrc = asset_path
    ? asset_path.startsWith('http')
      ? asset_path
      : staticFile(asset_path)
    : null;

  return (
    <AbsoluteFill style={{ backgroundColor: fallback_color }}>
      {/* Asset - full width for horizontal */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: caption ? 80 : 0,
          overflow: 'hidden',
          transform: `scale(${scale})`,
          transformOrigin: 'center center',
        }}
      >
        {resolvedSrc ? (
          asset_type === 'image' ? (
            <Img
              src={resolvedSrc}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
          ) : (
            <Video
              src={resolvedSrc}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
          )
        ) : (
          <div
            style={{
              width: '100%',
              height: '100%',
              backgroundColor: fallback_color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#F5F4F0',
              fontFamily: FONT,
              fontSize: 32,
              opacity: 0.5,
            }}
          >
            NO IMAGE
          </div>
        )}
      </div>

      {/* Caption - thinner bar for horizontal */}
      {caption && (
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: 80,
            backgroundColor: 'rgba(0,0,0,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: captionProgress,
          }}
        >
          <span
            style={{
              fontFamily: FONT,
              color: '#ffffff',
              fontSize: 28,
              fontWeight: 400,
              letterSpacing: '0.08em',
              textAlign: 'center',
              padding: '0 60px',
            }}
          >
            {caption}
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
}
