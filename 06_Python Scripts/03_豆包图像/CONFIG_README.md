# 封面生成引擎配置说明

## 概述

`cover_config.json` 是封面生成引擎的核心配置文件，实现了代码与排版参数的解耦。修改配置文件即可调整字号、间距、颜色等参数，无需修改 Python 源码。

---

## 配置文件结构

### 1. 画布尺寸 (`canvas`)

```json
{
  "width": 1080,
  "height": 1440,
  "aspect_ratio": "3:4"
}
```

- **width/height**: 画布尺寸（像素）
- **aspect_ratio**: 宽高比（抖音/小红书标准）

---

### 2. 布局参数 (`layout`)

```json
{
  "image_end": 700,
  "text_bg_start": 560,
  "text_area_top": 600,
  "margin_left": 80,
  "margin_right": 80
}
```

- **image_end**: 图片区域结束位置（Y轴）
- **text_bg_start**: 白底渐变过渡起始位置
- **text_area_top**: 文字区域顶部
- **margin_left/right**: 左右边距

---

### 3. 字号配置 (`fonts`)

#### 海报模式 (`poster`)
```json
{
  "title": 120,      // 主标题
  "subtitle": 60,    // 副标题
  "meta": 40,        // 钩子文案/底部说明
  "brand": 14        // 品牌标识
}
```

#### 抖音模式 (`douyin`)
```json
{
  "title": 280,      // 主标题（极限暴增）
  "subtitle": 120,   // 副标题
  "meta": 0,         // 不显示
  "brand": 0         // 不显示
}
```

**调整建议**：
- 主标题字号建议保持在 100-300pt 之间
- 副标题字号建议为主标题的 40-50%
- 抖音模式字号应比海报模式大 2-2.5 倍

---

### 4. 间距配置 (`spacing`)

#### 海报模式 (`poster`)
```json
{
  "title_line_spacing": 30,        // 主标题行间距
  "subtitle_margin_top": 85,       // 主副标题间距
  "description_margin_top": 60     // 副标题到说明文案间距
}
```

#### 抖音模式 (`douyin`)
```json
{
  "title_line_spacing": 10,        // 紧凑行间距
  "subtitle_margin_top": 20,       // 紧凑模块间距
  "description_margin_top": 0      // 不显示说明文案
}
```

**调整建议**：
- 行间距建议为字号的 10-30%
- 模块间距建议为字号的 30-80%
- 抖音模式应使用更紧凑的间距

---

### 5. 定位配置 (`positioning`)

```json
{
  "poster": {
    "title_start_y_ratio": 0.35    // 主标题起始Y轴位置（画布高度的35%）
  },
  "douyin": {
    "title_start_y_ratio": 0.5     // 正中央（画布高度的50%）
  }
}
```

**调整建议**：
- 海报模式：0.3-0.4（中央偏上）
- 抖音模式：0.45-0.55（正中央）

---

### 6. 色彩系统 (`colors`)

```json
{
  "background": [245, 244, 240],   // #F5F4F0 羊皮纸白
  "ink": [45, 43, 42],             // #2D2B2A 暖炭灰
  "accent": [211, 107, 77],        // #D36B4D 赤陶土
  "peach": [230, 200, 181],        // #E6C8B5 灰桃色
  "meta": [102, 102, 102],         // #666666 底部说明灰色
  "light_gray": [224, 224, 224],   // #E0E0E0 浅灰（网格线）
  "white": [255, 255, 255]
}
```

**新古典人文主义色彩系统**：
- 主背景：羊皮纸白（温暖、柔和）
- 主文本：暖炭灰（深色但不刺眼）
- 点缀色：赤陶土（温暖的橙红色）

---

### 7. 风格配置 (`styles`)

每种风格包含 5 种颜色配置：

```json
{
  "title_color": [45, 43, 42],      // 主标题颜色
  "subtitle_color": [211, 107, 77], // 副标题颜色
  "accent_color": [211, 107, 77],   // 点缀色
  "meta_color": [102, 102, 102],    // 底部说明颜色
  "hook_color": [130, 125, 120]     // 顶部钩子文案颜色
}
```

**可用风格**：
- `whitespace-aesthetic` - 留白美学（Wiki 方案1）
- `grid-system` - 网格系统（Wiki 方案2）
- `contrast-impact` - 对比冲击（Wiki 方案3，推荐）
- `classic-print` - 古典印刷（兼容旧版）
- `organic-botanical` - 有机生命体（兼容旧版）
- `academic-grid` - 学术网格（兼容旧版）

---

### 8. 平台特性 (`platform_features`)

```json
{
  "poster": {
    "show_concept": true,        // 显示H3概念文案
    "show_description": true,    // 显示底部说明
    "show_meta": true,           // 显示元信息
    "font_bold": false           // 不加粗
  },
  "douyin": {
    "show_concept": false,       // 隐藏H3概念文案
    "show_description": false,   // 隐藏底部说明
    "show_meta": false,          // 隐藏元信息
    "font_bold": true            // 加粗字体
  }
}
```

---

## 常见调整场景

### 场景1：抖音封面字号太小

**问题**：抖音版封面在手机上看不清

**解决方案**：
```json
{
  "fonts": {
    "douyin": {
      "title": 320,      // 从 280 增加到 320
      "subtitle": 140    // 从 120 增加到 140
    }
  }
}
```

---

### 场景2：海报版信息过于拥挤

**问题**：海报版文字间距太紧

**解决方案**：
```json
{
  "spacing": {
    "poster": {
      "title_line_spacing": 40,        // 从 30 增加到 40
      "subtitle_margin_top": 100,      // 从 85 增加到 100
      "description_margin_top": 80     // 从 60 增加到 80
    }
  }
}
```

---

### 场景3：主标题位置偏上/偏下

**问题**：主标题在画面中的位置不理想

**解决方案**：
```json
{
  "positioning": {
    "poster": {
      "title_start_y_ratio": 0.4    // 从 0.35 调整到 0.4（向下移动）
    },
    "douyin": {
      "title_start_y_ratio": 0.45   // 从 0.5 调整到 0.45（向上移动）
    }
  }
}
```

---

### 场景4：更换品牌色系

**问题**：需要使用不同的品牌色

**解决方案**：
```json
{
  "colors": {
    "accent": [0, 123, 255],    // 改为蓝色
    "peach": [200, 220, 240]    // 改为浅蓝色
  },
  "styles": {
    "contrast-impact": {
      "subtitle_color": [0, 123, 255],  // 副标题改为蓝色
      "accent_color": [0, 123, 255]     // 点缀色改为蓝色
    }
  }
}
```

---

## 配置验证

修改配置后，运行以下命令验证：

```bash
# 测试海报版
py auto_cover_engine.py --title "测试标题" --concept "测试概念" --platform poster --output test_poster.png

# 测试抖音版
py auto_cover_engine.py --title "测试标题" --concept "测试概念" --platform douyin --output test_douyin.png
```

---

## 注意事项

1. **JSON 格式**：修改配置文件时注意保持 JSON 格式正确（逗号、引号、括号）
2. **颜色格式**：颜色使用 RGB 数组格式 `[R, G, B]`，取值范围 0-255
3. **比例参数**：`title_start_y_ratio` 使用小数（0.0-1.0），表示画布高度的百分比
4. **字号单位**：所有字号单位为 pt（点）
5. **间距单位**：所有间距单位为 px（像素）

---

## 配置备份

修改配置前，建议先备份：

```bash
cp cover_config.json cover_config.json.backup
```

如需恢复：

```bash
cp cover_config.json.backup cover_config.json
```

---

## 技术细节

### 配置加载流程

1. `auto_cover_engine.py` 启动时自动加载 `cover_config.json`
2. 配置数据存储在全局变量 `CONFIG` 中
3. 渲染函数根据 `platform` 参数动态读取对应配置
4. 配置文件不存在时会抛出 `FileNotFoundError`

### 配置优先级

1. 命令行参数（最高优先级）
2. 配置文件参数
3. 代码中的硬编码默认值（最低优先级）

---

## 更新日志

### v1.0.0 (2026-04-15)
- 初始版本
- 实现代码与配置解耦
- 支持 poster 和 douyin 两种平台模式
- 支持 6 种视觉风格
- 完整的字号、间距、颜色配置
