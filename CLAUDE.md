# 水星艺术馆 — Claude Code 操作规则

## 死命令

- **根目录零文件** — 所有文件放对应子目录，临时文件用完即删（GC）
- **Python → `06_Python Scripts/`** — .py 文件禁止散落他处，禁止在全局库运行 Python
- **封面 3:4 (1080×1440)** — 禁止 16:9 横屏
- **色彩系统** — 主背景 `#F5F4F0` / 主文本 `#2D2B2A` / 点缀色 `#D36B4D`，禁止高饱和渐变/重阴影/发光，必须加 2-5% 噪点
- **禁止向 `03_Assets_全局库/` 写知识文档** — 该目录仅供资产（BGM/封面），知识文档放 `Wiki知识库/`
- **遇错先查 `.claude/lessons.md` 和 `memory/feedback_*.md`** — 不从零诊断
- **任务结束三步** — ①更新目录结构 ②整理文件到对应目录 ③教训写入 memory/

## 数据完整性

- **禁止凭空编造** — 产品故事、金句、色彩名称、数据必须从已有素材提取，不得虚构
- **缺数据先问** — 遇到缺失的具体数值或信息，标记为 `[NEEDS INPUT]` 并询问用户，禁止用占位符（X%、TODO）填充
- **引用标注来源** — 事实性断言须注明出处（wiki 页面/产品文件/参考数据）
- **文案须可溯源** — 生成内容中的每个具体细节都能指向一个已有的源文件

## 测试与验证

- **代码生成后必须运行验证** — 脚本写出后立即执行，检查报错和输出，不通过不报告完成
- **视觉产出须自检** — 封面/图片生成后，列出验证清单逐项确认（文字无裁剪、颜色匹配、对齐正确），禁止目测代替验证
- **修复须实际确认** — 禁止声称"已修复"但未运行测试；修复后展示验证结果而非口头保证
- **遇死胡同快速止损** — 同类错误连续 3 次失败后，停止修补并提出替代方案，不再继续同一方向

## 开发规则

- **先搜索再造轮子** — 写新脚本前用 Glob/Grep 搜索项目中是否已有同类工具或 wiki 条目，优先扩展而非重建
- **延伸已有 Skill** — 新功能应挂载到已有 Skill 体系，不创建孤立脚本
- **遵守文件目录规范** — Python → `06_Python Scripts/`，临时文件用完即删

## 踩坑速查

| 现象 | 正确做法 |
|------|----------|
| `ln -s` 目录变成实体文件夹 | `cmd //c "mklink /D <link> <target>"`，`ls -l` 验证首字母 `l` |
| Python 返回 exit 49 | 用 Node.js 做 JSON/文件处理，禁止反复重试 |
| Kitta TTS 返回二进制非 JSON | 先检测 Content-Type，按二进制下载逻辑降级 |
| `python` 命令指向 Windows Store stub | 必须用完整路径 `C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe` |
| 配音文件输出到脚本目录 | 必须输出到 `01_Projects_制作中/{产品名}/03_配音_音频/` |
| Write 工具写大文件报错 | 分章节生成（`_chN_temp.md`），PowerShell 追加，禁止一次性写入 |
| 分析数据直接跑脚本 | 先 `print` 前 10 行原始内容 |
| Bash→PowerShell 传中文乱码 | 两端指定编码 `Get-Content/Add-Content -Encoding UTF8` |

## 速查表

### Python 脚本

| 脚本 | 路径 |
|------|------|
| Todoist | `06_Python Scripts/07_Todoist/todoist_api.py` |
| 豆包图生图 | `06_Python Scripts/03_豆包图像/doubao_img2img.py` |
| 飞书上传 | `06_Python Scripts/02_飞书工具/feishu_update_*.py` |
| Perplexity 搜索 | `06_Python Scripts/05_搜索API/perplexity_search.py` |
| OpenRouter | `06_Python Scripts/05_搜索API/openrouter_agent.py` |
| Kitta TTS | `06_Python Scripts/06_工具/tts_kitta_refactored.py` |
| Wiki Lint | `06_Python Scripts/06_工具/wiki_lint.py` |

执行：`"C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" <脚本路径>`

### CLI 工具

| 工具 | 用途 |
|------|------|
| lark-cli | 飞书操作（`npx @larksuite/cli`），`lark-cli config init` 重新加载配置 |
| Wiki Lint | 知识库健康检查（`python wiki_lint.py`），覆盖 11 个维度 |

### 文件路径

| 用途 | 路径 |
|------|------|
| 产品背景 | `Wiki知识库/wiki/文案创作/选题库/{产品名}-文案参考资料.md` |
| 文案配置 | `Wiki知识库/wiki/文案创作/文案生成配置.md` |
| 封面规则 | `Wiki知识库/wiki/视频制作/封面设计规则.md` |
| 配音规范 | `Wiki知识库/wiki/视频制作/TTS配音系统使用指南.md` |
| BGM 库 | `Wiki知识库/assets/BGM音乐库/` |
| 知识库索引 | `Wiki知识库/index.md` |
| 收件箱 | `00_InBox_收件箱/` |
| Remotion 渲染 | `06_Python Scripts/04_自动代码工具箱/mercury-vis/` |

### 代理（GitHub 不可达时）

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```
备用端口：1080 → 10809 → 8080

## 工作流

**核心链路**：选品 → `/copywriter` 文案 → DBS 检定 → 飞书上传 → 配音(Kitta API) → 视频制作(外包) → 发布 → 数据追踪 → 周复盘

**配音默认 Kitta API**（S2 模型），GPT-SoVITS 未安装不可用，Mimo TTS 永久禁用

**文案产出标准**：
- 三套风格：余上沅的奇妙屋 / 九厘米的雾 / Ad Scout
- 命名：`01_Projects_制作中/{产品名}/MMDD-{产品名}-三套文案.md`
- 同步产出：视频标题 + 商品短标题 + 产品简介（不可拆分到后续流程）
- 必须指定 BGM 具体 MP3 路径

## 规则

- **先确认方案再动手** — 改代码前向用户说明计划
- **ICS 日历标配** — 日程类操作生成 .ics 文件
- **禁止 print 用 emoji**
- **禁止口算** — 数值计算写 Python 脚本，统一单位，stdout 提取，矛盾即中断
- **DBS 检定闭环** — 文案后 `/dbs-content`，用户 Approve 后才可配音/上传飞书
- **Skill 摩擦** — 遇摩擦立即问是否更新 Skill
- **站立规则** — "晚安"/"任务完成" → 更新 MEMORY.md + CLAUDE.md
- **收件箱清理** — 用户说"全部删除"直接执行，无需逐个确认
- **数据分析工作流** — 下载→放 `04_数据分析结果/`→分析提炼→有价值内容写入 wiki→原始数据删除

## 详细文档

| 文档 | 内容 |
|------|------|
| `.claude/lessons.md` | 历史教训（按日期倒序） |
| `.claude/workflows.md` | 10 步选品 + AI 文案流程 |
| `.claude/integrations.md` | 飞书 / Todoist / GitNexus 配置 |
| `.claude/project-structure.md` | 完整目录结构与保护规则 |
| `memory/MEMORY.md` | 项目记忆索引 |
| `Wiki知识库/index.md` | 知识库索引 |
