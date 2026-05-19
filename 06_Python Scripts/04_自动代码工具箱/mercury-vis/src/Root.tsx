import { Composition } from 'remotion';
import { registerRoot } from 'remotion';
import React from 'react';
import { Intro } from './components/Intro';
import { Transition } from './components/Transition';
import { TextReveal } from './shots/TextReveal';
import { ImageShowcase } from './shots/ImageShowcase';
import { DataHighlight } from './shots/DataHighlight';
import { BrainVisualization } from './shots/BrainVisualization';
import { EyeTracking } from './shots/EyeTracking';
import { VisualGuide } from './shots/VisualGuide';
import { ArrowGuide } from './shots/ArrowGuide';
import { ElementAttraction } from './shots/ElementAttraction';
import { CompositionAnnotation } from './shots/CompositionAnnotation';
import { GoldenRatio } from './shots/GoldenRatio';
import { LightbulbMoment } from './shots/LightbulbMoment';
import { FourElements } from './shots/FourElements';
import { VisualScanAnimation } from './01_visual_scan_animation';
import { CompositionLinesAnimation } from './02_composition_lines_animation';
import { DataVisualizationAnimation } from './03_data_visualization_animation';
import { FourElementsAnimation } from './04_four_elements_animation';
import { CommentArrowAnimation } from './05_comment_arrow_animation';

// ==========================================
// 根组件 - 1920x1080 横屏 16:9
// ==========================================
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MercuryIntro"
        component={Intro}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          mainTitle: '艺术的边界',
          subTitle: '探索当代艺术与古典美学的交融',
          volNumber: 'VOL.01',
        }}
      />
      <Composition
        id="MercuryTransition"
        component={Transition}
        durationInFrames={15}
        fps={30}
        width={1920}
        height={1080}
      />
      {/* TextReveal Shot */}
      <Composition
        id="TextReveal"
        component={TextReveal}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
      />
      {/* ImageShowcase Shot */}
      <Composition
        id="ImageShowcase"
        component={ImageShowcase}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      {/* DataHighlight Shot */}
      <Composition
        id="DataHighlight"
        component={DataHighlight}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />
      {/* Photography Infographic Animations */}
      <Composition
        id="BrainVisualization"
        component={BrainVisualization}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="EyeTracking"
        component={EyeTracking}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="VisualGuide"
        component={VisualGuide}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="ArrowGuide"
        component={ArrowGuide}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="ElementAttraction"
        component={ElementAttraction}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="CompositionAnnotation"
        component={CompositionAnnotation}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="GoldenRatio"
        component={GoldenRatio}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="LightbulbMoment"
        component={LightbulbMoment}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="FourElements"
        component={FourElements}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      {/* New Photography Animations - 1080x1920 Portrait */}
      <Composition
        id="VisualScan"
        component={VisualScanAnimation}
        durationInFrames={210}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="CompositionLines"
        component={CompositionLinesAnimation}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="DataVisualization"
        component={DataVisualizationAnimation}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="FourElementsNew"
        component={FourElementsAnimation}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="CommentArrow"
        component={CommentArrowAnimation}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};

registerRoot(RemotionRoot);
