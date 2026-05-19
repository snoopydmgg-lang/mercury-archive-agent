---
name: minimax-image
description: "使用 MiniMax 文生图 API 生成图片。示例：\"生成一张图\"、\"画一张图\"、\"帮我画一个海边日落\"、\"生成一张赛博朋克风格图片\""
---

# MiniMax 文生图工具

使用 MiniMax image-01 模型从文本生成图片。

## API 配置

| 配置项 | 值 |
|--------|-----|
| Base URL | `https://api.minimaxi.com/v1/image_generation` |
| API Key | `sk-cp-Ph7wF32ukEU5qR15Wt0Ra3uy0V6YDy7kAVto5XvbjJAGj4XQhCkwQzsueX_7skZMhym_rScVqUjS-PKM7sCWmIjI8jhwyYPB0rtKZDU47V76b5UaWgt4OBs` |
| 模型 | `image-01` |
| 代理 | `http://127.0.0.1:7890` |

## 脚本位置

`E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/minimax_image.py`

## 使用方式

### 命令行

```bash
"C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/minimax_image.py" "<prompt>" [aspect_ratio] [n]
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| prompt | 英文描述 | 必填 |
| aspect_ratio | 宽高比 | 3:4 |
| n | 生成数量 | 1 |

### aspect_ratio 可选值

| 比例 | 尺寸 | 用途 |
|------|------|------|
| 1:1 | 1024x1024 | 方形 |
| 16:9 | 1280x720 | 横版视频 |
| 4:3 | 1152x864 | 横版 |
| 3:2 | 1248x832 | 横版摄影 |
| 3:4 | 864x1152 | 竖版 |
| 2:3 | 832x1248 | 竖版人像 |
| 9:16 | 720x1280 | 竖版视频 |
| 21:9 | 1344x576 | 超宽 |

### 模型

| 模型 | 说明 |
|------|------|
| image-01 | 标准模型，支持所有比例 |
| image-01-live | 支持画风风格：漫画、元气、中世纪、水彩 |

### 示例

```bash
# 生成海边日落图
"C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/minimax_image.py" "A beautiful sunset over the ocean with golden reflection, photorealistic photography" "16:9" 1

# 生成赛博朋克风格
"C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/minimax_image.py" "Cyberpunk city at night, neon lights, rainy streets, blade runner style, cinematic" "16:9" 1

# 生成书籍封面(竖版)
"C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/minimax_image.py" "Elegant book cover design, minimalist art style, soft pastel colors, modern aesthetic" "3:4" 1
```

## 输出

生成成功后返回图片 URL，有效期 24 小时。
