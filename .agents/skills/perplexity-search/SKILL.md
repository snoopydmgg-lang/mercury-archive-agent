---
name: perplexity-search
description: "使用 OpenRouter API 调用 Perplexity Sonar 进行深度研究搜索。示例：\"帮我查一下xxx\", \"查找xxx的确切资料\", \"深入研究xxx\", \"帮我确认xxx的具体信息\""
---

# Perplexity 深度搜索工具

使用 OpenRouter API 调用 **Perplexity Sonar** 模型进行深度研究和资料查找。

**本脚本只做一件事：深度搜索查找确切资料。不负责其他任何任务。**

## 功能

| 功能 | 说明 |
|------|------|
| 普通搜索 | 使用 perplexity/sonar 快速搜索（轻量级） |
| 深度搜索 | 使用 perplexity/sonar-pro 深度研究（最先进） |
| 事实查证 | 查找确切资料、数据、来源 |
| 深度研究 | 深入分析复杂问题 |
| 多角度查询 | 支持追问和深入挖掘 |

## 代码位置

`E:\1.work\douyin\1.shuixing\06_Python Scripts\perplexity_search.py`

## 输入输出规则

- **输入**: 用户的问题或搜索请求
- **输出**: 模型生成的回答（包含引用来源）

## 使用方法

### 基本流程

1. **理解用户需求** - 用户需要查找确切资料时使用
2. **构建查询** - 将用户问题作为搜索查询
3. **运行脚本**:
   ```bash
   cd "E:/1.work/douyin/1.shuixing/06_Python Scripts"
   python perplexity_search.py "<搜索内容>"
   ```
4. **返回结果** - 将搜索结果展示给用户

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| `query` | 搜索查询内容 | 是 |
| `--deep`, `-d` | 使用深度搜索模式（sonar-pro，更详细更全面） | 否 |
| `--no-search` | 禁用网络搜索，仅使用模型知识 | 否 |

### 使用场景

**适用场景**:
- 查找确切的数据、统计、数字
- 确认某个事实或信息
- 深入了解某个主题
- 研究某个领域的问题
- 查找参考资料

**不适用场景**:
- 简单的闲聊问题
- 本地文件内容分析（使用 grep/read 工具）
- 代码相关问题（使用 Agent/grep 工具）

### 示例

```bash
# 普通搜索（快速、轻量）
python perplexity_search.py "2024年中国新能源汽车销量数据"

# 深度搜索（更详细、更全面）
python perplexity_search.py "2024年中国新能源汽车销量数据" --deep

# 查找事实
python perplexity_search.py "莫奈《睡莲》的创作年份和收藏地点"

# 深度研究
python perplexity_search.py "人工智能对艺术创作的影响分析" --deep

# 禁用搜索（仅模型知识）
python perplexity_search.py "量子计算的基本原理" --no-search
```

### 交互式模式

不传参数时进入交互式模式：

```bash
python perplexity_search.py
```

## 注意事项

1. **网络依赖**: 需要联网才能获取最新资料
2. **等待时间**: 深度搜索可能需要较长时间（最多 2 分钟）
3. **API 配额**: 注意 API 调用次数限制
4. **结果验证**: 重要信息建议多角度验证
5. **中文支持**: 完全支持中文搜索和回答

## 触发关键词

当用户说以下话时使用此 skill：
- "帮我查一下"
- "查找"
- "确认"
- "深入了解"
- "研究一下"
- "具体是"
- "确切是"
- "帮我找"
- "资料"
- "数据"
- 其他需要查找确切资料的场景

### 普通搜索 vs 深度搜索

- **普通搜索**：直接使用 `perplexity/sonar` 模型，快速轻量
  - 示例：简单的事实查询、快速确认

- **深度搜索**：添加 `--deep` 参数使用 `perplexity/sonar-pro` 模型，最先进
  - 示例：复杂问题分析、深度研究报告
  - 关键词："深入研究"、"详细分析"、"全面了解"

## 依赖

```bash
pip install requests
```
