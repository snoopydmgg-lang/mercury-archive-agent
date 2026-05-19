import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 读取合并数据
with open('.graphify_semantic_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取 AST 数据
ast_nodes = 1007
ast_edges = 2135

# 统计分析
file_summaries = data['file_summaries']
all_concepts = []
all_deps = []

for path, info in file_summaries.items():
    all_concepts.extend(info.get('key_concepts', []))
    all_deps.extend(info.get('dependencies', []))

concept_freq = Counter(all_concepts)
dep_freq = Counter(all_deps)

# 按目录分类
dir_stats = {}
for path in file_summaries.keys():
    parts = path.replace('\\', '/').split('/')
    dir_name = parts[0] if len(parts) > 1 else 'root'
    dir_stats[dir_name] = dir_stats.get(dir_name, 0) + 1

# 生成报告
report = f'''# Python 脚本库知识图谱分析报告

生成时间: 2026-04-17
分析路径: E:/1.work/douyin/1.shuixing/06_Python Scripts

## 📊 整体统计

- **文件总数**: {data['total_files']} 个
- **AST 节点**: {ast_nodes} 个
- **AST 边**: {ast_edges} 条
- **语义实体**: {data['total_entities']} 个
- **语义关系**: {data['total_relationships']} 条
- **识别概念**: {len(concept_freq)} 个
- **依赖模块**: {len(dep_freq)} 个

## 📁 目录分布

'''

for dir_name, count in sorted(dir_stats.items(), key=lambda x: -x[1])[:10]:
    report += f'- `{dir_name}`: {count} 个文件\n'

report += f'''

## 🔑 核心概念 (Top 15)

'''

for concept, count in concept_freq.most_common(15):
    report += f'- **{concept}**: {count} 次\n'

report += f'''

## 📦 主要依赖 (Top 15)

'''

for dep, count in dep_freq.most_common(15):
    report += f'- `{dep}`: {count} 次\n'

report += f'''

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

'''

if data['relationships']:
    for rel in data['relationships'][:10]:
        source = rel.get('source', '?')
        rel_type = rel.get('type', '?')
        target = rel.get('target', '?')
        report += f'- {source} → {rel_type} → {target}\n'

report += f'''

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
'''

# 保存报告
with open('Python脚本库_知识图谱报告.md', 'w', encoding='utf-8') as f:
    f.write(report)

print('Report generated: Python脚本库_知识图谱报告.md')
print(f'Total lines: {len(report.splitlines())}')
