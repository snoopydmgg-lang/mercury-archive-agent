#!/usr/bin/env node
/**
 * 批量渲染脚本 - 每个镜头独立bundle确保props更新
 */

const fs = require('fs');
const path = require('path');

const { bundle } = require('@remotion/bundler');
const { selectComposition, renderMedia } = require('@remotion/renderer');

const OUTPUT_DIR = path.join(__dirname, 'dist');
const ENTRY_POINT = path.join(__dirname, 'src', 'Root.tsx');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const dataFile = path.join(__dirname, 'video_data.json');
const VIDEO_DATA = JSON.parse(fs.readFileSync(dataFile, 'utf-8'));
console.log(`📄 数据文件: ${dataFile}`);

function getCompositionId(type) {
  const mapping = {
    'text_reveal': 'TextReveal',
    'image_showcase': 'ImageShowcase',
    'data_highlight': 'DataHighlight',
    'intro': 'MercuryIntro',
    'transition': 'MercuryTransition',
    'brain_visualization': 'BrainVisualization',
    'eye_tracking': 'EyeTracking',
    'visual_guide': 'VisualGuide',
    'arrow_guide': 'ArrowGuide',
    'element_attraction': 'ElementAttraction',
    'composition_annotation': 'CompositionAnnotation',
    'golden_ratio': 'GoldenRatio',
    'lightbulb_moment': 'LightbulbMoment',
    'four_elements': 'FourElements',
  };
  return mapping[type] || type;
}

function buildInputProps(shot) {
  const props = {
    text_main: shot.text_main || '',
    text_sub: shot.text_sub || '',
    bg_color: shot.bg_color || '#1a1a2e',
    text_color: shot.text_color || '#ffffff',
    duration_sec: shot.duration_sec || 4,
  };
  if (shot.accent_color) {
    props.accent_color = shot.accent_color;
  }
  console.log(`   [DEBUG] inputProps:`, JSON.stringify(props));
  return props;
}

async function renderShot(shot, index) {
  const outputName = `shot_${String(index + 1).padStart(2, '0')}.mp4`;
  const outputPath = path.join(OUTPUT_DIR, outputName);

  console.log(`\n[镜头${index + 1}] 类型: ${shot.type}`);
  console.log(`   内容: ${shot.text_main || shot.caption || shot.number || 'N/A'}`);

  try {
    // 每个镜头都重新创建bundle，确保最新的video_data.json被读取
    console.log(`   正在打包源码 (镜头${index + 1})...`);
    const serveUrl = await bundle({
      entryPoint: path.resolve(ENTRY_POINT),
      // 禁用缓存
      webpackDefines: {
        'process.env.NODE_ENV': JSON.stringify('production'),
      },
    });
    console.log(`   打包完成: ${serveUrl}`);

    const compId = getCompositionId(shot.type);
    console.log(`   查找 Composition: ${compId}`);

    const composition = await selectComposition({
      serveUrl,
      id: compId,
    });

    if (!composition) {
      throw new Error(`未找到 Composition: ${compId}`);
    }

    const inputProps = buildInputProps(shot);

    console.log(`   开始渲染 (frames: ${Math.ceil((shot.duration_sec || 4) * 30)})...`);

    await renderMedia({
      serveUrl,
      composition,
      inputProps,
      outputLocation: path.resolve(outputPath),
      codec: 'h264',
      crf: 18,
    });

    const stats = fs.statSync(outputPath);
    console.log(`   ✅ 完成: ${outputPath} (${stats.size} bytes)`);
    return { success: true, output: outputPath };
  } catch (err) {
    console.error(`   ❌ 失败: ${err.message}`);
    console.error(err.stack);
    return { success: false, error: err.message };
  }
}

async function main() {
  console.log('═══════════════════════════════════════');
  console.log('水星艺术馆 - 镜头渲染 (独立bundle模式)');
  console.log('═══════════════════════════════════════');

  if (VIDEO_DATA.shots && Array.isArray(VIDEO_DATA.shots)) {
    console.log(`\n检测到多镜头数据，共 ${VIDEO_DATA.shots.length} 个镜头`);
    console.log(`输出目录: ${OUTPUT_DIR}`);

    let success = 0;
    for (let i = 0; i < VIDEO_DATA.shots.length; i++) {
      const result = await renderShot(VIDEO_DATA.shots[i], i);
      if (result.success) success++;
    }

    console.log('\n═══════════════════════════════════════');
    console.log(`完成: ${success}/${VIDEO_DATA.shots.length} 个镜头`);
    console.log('═══════════════════════════════════════');
  }
}

main();
