# 水星艺术馆 — Claude Code Agent 配置

## Agent 行为规则

- 根目录零文件 — 所有文件放对应子目录，临时文件用完即删
- 封面 3:4 (1080×1440) — 禁止 16:9 横屏
- 色彩系统 — 主背景 #F5F4F0 / 主文本 #2D2B2A / 点缀色 #D36B4D，禁止高饱和渐变/重阴影/发光
- 遇错先查 .claude/lessons.md 和 memory/ — 不从零诊断
- 任务结束三步 — 更新目录结构 → 整理文件 → 教训写入 memory/

## 模型调度策略

| 任务类型 | 调度模型 |
|----------|----------|
| 长链推理、文案创作、内容检定 | Claude Opus/Sonnet |
| 批量数据提取、关键词分析 | DeepSeek 系列 |
| 图像生成、语音合成 | MiniMax (豆包 API / TTS) |

## 外部集成

- 飞书开放平台 (文档/表格/日历/知识库/即时通讯)
- 豆包图生图 API
- Perplexity Search API
- Todoist Task API
- Kitta TTS / GPT-SoVITS
- OpenRouter (多模型路由)

## 自愈机制

Agent 在生产环境中积累的错误修复规则（部分）：

| 现象 | 正确做法 |
|------|----------|
| `python` 指向 Windows Store stub | 使用完整路径 `C:/.../Python310/python.exe` |
| Kitta TTS 返回二进制非 JSON | 先检测 Content-Type，按二进制下载逻辑降级 |
| 配音文件输出到脚本目录 | 强制输出到项目文件夹 |
| Bash→PowerShell 传中文乱码 | 两端指定 UTF-8 编码 |
