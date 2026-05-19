# Python 脚本库知识图谱分析报告

生成时间: 2026-04-17
分析路径: E:/1.work/douyin/1.shuixing/06_Python Scripts

## 📊 整体统计

- **文件总数**: 75 个
- **AST 节点**: 1007 个
- **AST 边**: 2135 条
- **语义实体**: 31 个
- **语义关系**: 21 条
- **识别概念**: 98 个
- **依赖模块**: 24 个

## 📁 目录分布

- `01_AI文案`: 37 个文件
- `02_飞书工具`: 28 个文件
- `root`: 10 个文件


## 🔑 核心概念 (Top 15)

- **Kitta AI**: 8 次
- **text-to-speech**: 7 次
- **audio generation**: 7 次
- **Claude API**: 4 次
- **Miyazaki content**: 3 次
- **three styles**: 3 次
- **prompt template**: 3 次
- **poetry narration**: 2 次
- **Tagore**: 2 次
- **BGM recommendation**: 2 次
- **OpenAI API**: 2 次
- **content diagnosis**: 2 次
- **DBS framework**: 2 次
- **Feishu integration**: 2 次
- **copywriting generation**: 2 次


## 📦 主要依赖 (Top 15)

- `sys`: 29 次
- `os`: 24 次
- `io`: 24 次
- `re`: 16 次
- `requests`: 15 次
- `json`: 15 次
- `time`: 8 次
- `datetime`: 7 次
- `openai`: 7 次
- `pathlib`: 5 次
- `config`: 5 次
- `anthropic`: 3 次
- `traceback`: 3 次
- `json_repair`: 3 次
- `copyworkflow.audio_generator`: 2 次


## 🎯 核心功能模块

### 1. AI 文案生成系统
- **copyworkflow**: 完整的内容生产流水线
- **三大风格模板**: 余上沅（学术深度）、九厘米的雾（内行视角）、Ad Scout（知识焦虑营销）
- **质量控制**: DBS 检查点、数据驱动优化（基于 1.1% 完成率）
- **集成服务**: Claude（脚本）、Kitta AI（TTS）、Perplexity（背景研究）、Feishu（协作）

### 2. 飞书集成工具
- **产品线**: 版式之道、飞鸟集、宫崎骏、我等你、摄影构图艺术
- **自动化评分**: 转化率、佣金、商家评分 → 重点跟进/可尝试/一般
- **Bitable 作为内容中心**: 视频制作流程的单一数据源

### 3. 视觉设计系统
- **封面生成器**: 分形图案生成（8 种递归模式）
- **品牌色彩系统**: #F5F4F0（背景）、#2D2B2A（主文字）、#D36B4D（强调色）
- **严格约束**: 3:4 比例、极简美学、禁止人物出现

### 4. 知识库管理工具
- **WikiLint**: 11+ 维度健康检查（死链、孤岛、前置元数据、命名规范）
- **Obsidian 增强版**: 双链/Canvas/图谱连通性检查（DFS 算法）
- **横向链接生成器**: Jaccard 相似度 + 加权组合算法

### 5. 数据分析工具
- **抖音数据分析**: 博主作品、整体统计、新内容监控
- **产品选品爬虫**: 多平台支持、评分系统、Feishu 导入
- **Excel 批量分析**: 数据质量评估、结构报告生成

### 6. 多模态分析
- **VideoAnalyzer**: 关键帧提取（OpenCV）+ Whisper 转写 + Claude Vision API
- **屏幕内容提取**: 透视变换、计算机视觉

## 🔗 关键依赖关系

- ? → uses → ?
- ? → uses → ?
- ? → calls → ?
- ? → extends → ?
- ? → calls → ?
- ? → controls → ?
- ? → analyzes → ?
- ? → contains → ?
- ? → contains → ?
- ? → uses → ?


## 💡 技术洞察

1. **迭代开发文化**: 多个工具存在 v2-v20 版本，表明快速原型开发
2. **中文编码处理**: UTF-8 包装模式在 9+ 文件中重复出现
3. **硬编码问题**: API 密钥和代理设置分散在多个文件中
4. **缺少抽象层**: 飞书认证逻辑在多个脚本中重复

## 📈 优化建议

1. **统一配置管理**: 将 API 密钥、代理设置集中到配置文件
2. **抽象公共逻辑**: 提取飞书认证、API 调用等公共模块
3. **版本控制**: 清理过时版本，保留稳定版本
4. **错误处理**: 增加重试机制和错误恢复逻辑
5. **文档完善**: 为核心模块添加使用文档

---

**生成工具**: Graphify v0.4.19
**分析引擎**: Claude Sonnet 4.6
