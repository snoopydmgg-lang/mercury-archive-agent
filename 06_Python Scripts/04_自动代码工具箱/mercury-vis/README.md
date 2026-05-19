# 水星艺术馆 - 视频渲染工具

基于 Remotion 的横屏视频自动渲染工具，支持多种镜头组件。

**规格：1920×1080（横屏 16:9）**

---

## 一、环境准备

```bash
cd mercury-vis
npm install
```

---

## 二、启动预览

```bash
cd mercury-vis
npx remotion preview src/Root.tsx
```

浏览器访问：http://localhost:3000

---

## 三、支持的镜头类型

| 类型 | 文件 | 功能 |
|------|------|------|
| 开场动画 | `Intro.tsx` | 主标题 + 副标题淡入 |
| 转场 | `Transition.tsx` | 色块滑入滑出 |
| 文字展示 | `shots/TextReveal.tsx` | 文字从下往上淡入 |
| 图片展示 | `shots/ImageShowcase.tsx` | Ken Burns 效果 + 字幕 |
| 数据强调 | `shots/DataHighlight.tsx` | 数字弹跳出现 |

---

## 四、数据格式

编辑 `video_data.json`：

```json
{
  "shots": [
    {
      "id": 1,
      "type": "text_reveal",
      "duration_sec": 4,
      "text_main": "留白，不是空着",
      "text_sub": "日本设计师的留白哲学",
      "bg_color": "#1a1a2e",
      "text_color": "#ffffff"
    },
    {
      "id": 2,
      "type": "image_showcase",
      "duration_sec": 5,
      "asset_path": "assets/test.jpg",
      "caption": "18位日本设计大师亲自指导",
      "asset_type": "image"
    },
    {
      "id": 3,
      "type": "data_highlight",
      "duration_sec": 3,
      "number": "18",
      "unit": "位大师",
      "description": "亲自指导",
      "bg_color": "#0f3460",
      "accent_color": "#e94560"
    }
  ]
}
```

---

## 五、渲染导出

```bash
node batch_render.js
```

输出：`dist/shot_01.mp4`、`shot_02.mp4`、`shot_03.mp4`...

---

## 六、图片素材路径

**重要：** Remotion 加载本地图片需要将素材放在 `public/` 目录下：

```
mercury-vis/
├── public/
│   └── assets/          ← 图片放这里
│       └── test.jpg
├── src/
└── batch_render.js
```

使用 `staticFile('assets/test.jpg')` 或直接写相对路径。

---

## 七、文件结构

```
mercury-vis/
├── public/
│   └── assets/              # 静态素材（图片/视频）
├── src/
│   ├── Root.tsx              # 入口，注册所有 Composition
│   ├── components/
│   │   ├── Intro.tsx         # 开场动画
│   │   └── Transition.tsx     # 转场
│   └── shots/
│       ├── TextReveal.tsx     # 文字展示
│       ├── ImageShowcase.tsx   # 图片展示
│       └── DataHighlight.tsx  # 数据强调
├── batch_render.js            # 渲染脚本
├── video_data.json           # 数据配置
└── README.md
```

---

## 八、常见报错

| 报错 | 解决 |
|------|------|
| 图片 404 | 确认图片在 `public/` 目录，路径正确 |
| View/Text undefined | 使用 `div`/`span` 替代 |
| codec undefined | `renderMedia()` 传 `codec: 'h264'` |
| useContext null | 组件改用 `function` 声明 |
