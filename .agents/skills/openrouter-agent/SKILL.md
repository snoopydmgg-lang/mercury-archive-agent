---
name: openrouter-agent
description: "使用 OpenRouter API 调用多种 AI 模型。示例：\"用OpenRouter问个问题\", \"调用gpt\", \"切换到deepseek模型\", \"列出可用模型\""
---

# OpenRouter 多模型 Agent

使用 OpenRouter API 通过单一端点访问数百个 AI 模型，自动处理备份并选择最具成本效益的选项。

**本脚本只做一件事：多模型对话。不负责其他任何任务。**

## 功能

| 功能 | 说明 |
|------|------|
| 多模型支持 | 访问数百个 AI 模型（OpenAI、Anthropic、Google、DeepSeek 等） |
| 级别选择 | 按需求选择 free / fast / balanced / pro / reasoning / search 级别 |
| 自动选择 | 每个级别自动选择最具性价比的模型 |
| 使用统计 | 显示实际使用的 tokens 数量 |

## 代码位置

`E:\1.work\douyin\1.shuixing\06_Python Scripts\openrouter_agent.py`

## 模型级别

| 级别 | 说明 | 推荐场景 |
|------|------|---------|
| `free` | 免费模型 | 测试、简单问题 |
| `fast` | 快速低成本 | 日常对话、快速响应 |
| `balanced` | 性价比最佳 | 通用场景（默认） |
| `pro` | 高性能 | 复杂问题、高质量回答 |
| `reasoning` | 推理模型 | 逻辑分析、数学问题 |
| `search` | 搜索模型 | 实时信息查询 |

## 使用方法

### 基本流程

1. **理解需求** - 判断用户需要的模型级别
2. **运行脚本**:
   ```bash
   cd "E:/1.work/douyin/1.shuixing/06_Python Scripts"
   python openrouter_agent.py "<问题内容>"
   ```
3. **返回结果** - 展示回答和 tokens 使用情况

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| `prompt` | 对话内容 | 是 |
| `--model` / `-m` | 指定模型 ID | 否 |
| `--tier` / `-t` | 模型级别 (free/fast/balanced/pro/reasoning/search) | 否 |
| `--system` / `-s` | 系统提示词 | 否 |
| `--list` / `-l` | 列出所有可用模型 | 否 |
| `--stream` | 流式输出 | 否 |

### 使用示例

```bash
# 列出所有可用模型
python openrouter_agent.py --list

# 使用默认平衡模型（balanced）
python openrouter_agent.py "什么是量子计算？"

# 使用免费模型
python openrouter_agent.py "你好" --tier free

# 使用推理模型
python openrouter_agent.py "分析这段代码的时间复杂度" --tier reasoning

# 使用搜索模型
python openrouter_agent.py "今天天气怎么样" --tier search

# 指定具体模型
python openrouter_agent.py "翻译这段话" --model "deepseek/deepseek-chat"

# 交互式模式
python openrouter_agent.py
```

## 当前可用模型

- **Free**: DeepSeek Chat, Llama 3.1 8B
- **Fast**: Qwen 2.5 72B, DeepSeek Chat, Codex 3 Haiku, Gemini 2.0 Flash
- **Balanced**: Codex 3.5 Sonnet, GPT-4o Mini, Gemini 2.0 Flash 002
- **Pro**: GPT-4o, Codex 3 Opus, Gemini 2.5 Pro
- **Reasoning**: DeepSeek R1, Codex 3.5 Sonnet
- **Search**: Perplexity Sonar, Perplexity Sonar Pro

## 注意事项

1. **API 配额**: 免费模型可能有调用限制
2. **地区限制**: 部分模型在特定地区不可用
3. **成本控制**: 默认使用 balanced 级别，性价比较高
4. **模型可用性**: 某些模型可能随时不可用，建议多熟悉几个备选模型

## 依赖

```bash
pip install requests
```

## 触发关键词

当用户说以下话时使用此 skill：
- "用 OpenRouter"
- "调用 gpt"
- "切换到 xx 模型"
- "列出可用模型"
- "用 xx 回答这个问题"
- 其他需要调用各种 AI 模型的场景
