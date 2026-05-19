---
name: ccswitch
description: "cc-switch Provider 切换工具。在多个 AI 模型 Provider 之间切换，并自动处理 Claude Pro 订阅修复。示例：\"换成 MiniMax\", \"切到 DeepSeek\", \"用官方订阅\", \"切回 Claude\", \"看看有哪些模型\""
---

# cc-switch Provider 切换工具

在 Claude Code / Codex / OpenClaw 的多个 AI Provider 之间切换，自动处理订阅缓存。

## 核心功能

| 功能 | 说明 |
|------|------|
| 列出 Provider | 显示所有可用 Provider（* 为当前激活） |
| 切换 Provider | 切换到指定 Provider |
| 切回官方订阅 | 切回 Claude Official + 自动修复订阅缓存 |
| 查看当前状态 | 显示当前激活的 Provider |
| 查看详情 | 显示 Provider 的端点/模型等信息 |

## 已配置 Provider

| App | Provider | 说明 |
|-----|----------|------|
| claude | **Claude Official** | 原生 Pro 订阅 |
| claude | OfoxAI | `api.ofox.ai` 中转 |
| claude | DeepSeek | DeepSeek V3.2 |
| claude | MiniMax | MiniMax M2.7 |
| codex | OfoxAI | Codex 专用 |
| openclaw | MiniMax M2.5 | OpenClaw 专用 |

## 代码位置

`E:\1.work\douyin\1.shuixing\06_Python Scripts\06_工具\ccswitch_cli.py`

## 使用方法

### 基本流程

1. 理解用户想切换到哪个 Provider
2. 执行对应命令
3. **如果切回 Claude Official，必须执行 fix-sub**
4. 提示用户重启 Claude Code（如果切回官方订阅）

### 命令语法

```bash
PYTHON="C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe"
SCRIPT="E:/1.work/douyin/1.shuixing/06_Python Scripts/06_工具/ccswitch_cli.py"

# 列出所有 Provider
"$PYTHON" "$SCRIPT" list
"$PYTHON" "$SCRIPT" list claude

# 查看当前激活
"$PYTHON" "$SCRIPT" current

# 切换到第三方 Provider
"$PYTHON" "$SCRIPT" use MiniMax
"$PYTHON" "$SCRIPT" use DeepSeek claude
"$PYTHON" "$SCRIPT" use OfoxAI

# 切回 Claude 官方订阅（自动修复缓存）
"$PYTHON" "$SCRIPT" fix-sub

# 查看 Provider 详情
"$PYTHON" "$SCRIPT" info MiniMax
```

## 关键规则

### 切第三方 Provider
直接执行 `use <名称>` 即可，不需要额外步骤。

### 切回 Claude Official（重要！）
**必须用 `fix-sub`，不能用 `use "Claude Official"`。**

原因：切第三方时 Claude Code 会缓存 `hasAvailableSubscription: False`，
`fix-sub` 会同时：
1. 切换到 Claude Official
2. 清除 `~/.claude/settings.json` 中的第三方 env 注入
3. 重置 `~/.claude.json` 的订阅缓存

执行完 `fix-sub` 后，**提示用户重启 Claude Code**。

## 触发关键词

- "换成 MiniMax / DeepSeek / OfoxAI"
- "切换模型"
- "用 MiniMax"
- "换个模型"
- "切回 Claude"
- "切回官方订阅"
- "用官方"
- "看看有哪些模型 / Provider"
- "现在用的哪个模型"
- "ccswitch"

## 注意事项

1. 切回 Claude Official 后必须**重启 Claude Code**才能生效
2. 切第三方 Provider 不需要重启，即时生效
3. `fix-sub` 不会损坏 Pro 订阅，OAuth Token 始终保留在 `.credentials.json`
