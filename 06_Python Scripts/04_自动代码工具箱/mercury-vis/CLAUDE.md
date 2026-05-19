# 自定义技能：生成视频开场

## 唤醒词

当用户输入类似 **"生成开场：[产品/主题]"** 的指令时，立即执行。

## 执行流程

1. **生成文案**：扮演资深文案，根据[产品/主题]生成 1 组符合"新古典人文主义"风格的主标题和副标题
2. **写入配置**：覆写 `video_data.json`
3. **执行渲染**：在终端执行 `node batch_render.js`
4. **返回结果**：完成后输出："✅ [产品/主题] 开场已生成，请前往 dist 目录提取 MP4。"

## 支持的主题类型

| 类型 | 示例 |
|------|------|
| 艺术/画家 | 梵高与星夜、莫奈的光影 |
| 文学/戏剧 | 莎士比亚的舞台、小王子 |
| 历史/文化 | 故宫建筑美学、中国传统色 |
| 科技/产品 | 三星S24影像对比 |
| 摄影/构图 | 镜头语言的视觉密码 |

## 技术约束（重要）

1. **分辨率**：固定 1920x1080（横屏 16:9），禁止竖屏
2. **HTML 标签**：Remotion 不提供 View/Text，请使用 `div`/`span`
3. **组件声明**：避免 `React.FC<>` 箭头函数，用 `function` 声明
4. **codec 参数**：`renderMedia()` 必须传 `codec: 'h264'`
5. **本地图片**：需放在 `public/assets/` 目录，使用 `staticFile()` 加载

## 视觉规范（必须遵守）

### 色彩系统
| 名称 | 色值 | 用途 |
|------|------|------|
| 主背景 | `#F5F4F0` | 暖米色背景 |
| 主文本 | `#2D2B2A` | 炭灰色文字 |
| 点缀色 | `#D36B4D` | 赤陶色强调 |

### 字体规范
**中文衬线（标题）**：`'Source Han Serif SC', 'Noto Serif CJK SC', 'Microsoft YaHei', Georgia, serif`
**无衬线（正文）**：`'Microsoft YaHei', '微软雅黑', Inter, sans-serif`

**注意**：font-family 链中，中文字体必须放在西文字体前面，否则浏览器无法正确渲染中文。

### 噪点纹理
封面和图片素材**必须**添加 2-5% 单色噪点或纸张纹理：
```xml
<filter id="noise">
  <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" stitchTiles="stitch"/>
  <feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.032 0"/>
</filter>
```

## 重要：Props 传递机制

### 数据流向
```
video_data.json → batch_render.js → inputProps → Remotion组件
```

`batch_render.js` 的 `buildInputProps()` 函数构建的 props 会通过 `inputProps` 参数传入 Remotion 组件。

### ⚠️ 禁止在 Composition 中使用 defaultProps
**错误示例**：
```tsx
<Composition
  id="TextReveal"
  component={TextReveal}
  durationInFrames={120}
  defaultProps={{
    bg_color: '#F5F4F0',  // ❌ 这些 defaultProps 会覆盖 inputProps！
    text_color: '#2D2B2A',
  }}
/>
```

**正确做法**：组件内部应该从 `inputProps` 读取所有配置，不要依赖 defaultProps：
```tsx
function TextReveal({ text_main, bg_color, text_color, ... }) {
  // 直接使用 props，不要设置 defaultProps
}
```

### 调试方法
`batch_render.js` 第45行有 DEBUG 日志，渲染时会打印传入的 inputProps。检查此项可确认数据是否正确传递。

## 文件位置

- 组件源码：`src/components/Intro.tsx`、`src/shots/*.tsx`
- 渲染脚本：`batch_render.js`
- 数据配置：`video_data.json`
- 静态素材：`public/assets/`
- 输出目录：`dist/`
