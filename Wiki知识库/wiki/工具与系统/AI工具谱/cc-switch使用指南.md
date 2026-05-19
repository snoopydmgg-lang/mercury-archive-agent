---
title: cc-switch 使用指南
tags:
  - AI工具
  - cc-switch
  - Provider切换
aliases:
  - cc-switch
  - Provider切换工具
关联笔记:
  - "[[大模型订阅指南]]"
录入日期: 2026-04-13
---

# cc-switch 使用指南

**来源**: 逆向分析 cc-switch v3.11 源码 + 数据库结构
**生成日期**: 2026-04-13
**关联**: [[大模型订阅指南]]

---

## 是什么

cc-switch 是一个 GUI 工具，用于在多个 AI Provider 之间切换，
支持 Claude Code / Codex / OpenClaw 等工具的 API 来源管理。

**数据路径**：
- 数据库：`C:\Users\Administrator\.cc-switch\cc-switch.db`
- 设置：`C:\Users\Administrator\.cc-switch\settings.json`

---

## 内部机制

### Provider 切换原理

切换 Provider 时，cc-switch 会：
1. 更新数据库 `providers.is_current` 字段
2. 更新 `settings.json` 中的 `currentProviderClaude`
3. **将 Provider 的 env 配置写入 `~/.claude/settings.json`**（关键！）

例如切到 MiniMax 时，`~/.claude/settings.json` 会被写入：
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-cp-...",
    "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
    "ANTHROPIC_MODEL": "MiniMax-M2.7"
  }
}
```

### 订阅失效原因

1. 第三方 Provider 激活 → Claude Code 用第三方节点检查订阅 → 返回 `hasAvailableSubscription: False`
2. 该状态缓存进 `~/.claude.json`
3. 切回 Claude Official 后，**缓存不自动清除**，订阅持续显示失效

---

## CLI 工具

路径：`06_Python Scripts/06_工具/ccswitch_cli.py`

```bash
PYTHON="C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe"
SCRIPT="06_Python Scripts/06_工具/ccswitch_cli.py"

# 列出所有 provider（* 为当前激活）
"$PYTHON" "$SCRIPT" list
"$PYTHON" "$SCRIPT" list claude

# 查看当前激活
"$PYTHON" "$SCRIPT" current

# 切换 provider
"$PYTHON" "$SCRIPT" use MiniMax
"$PYTHON" "$SCRIPT" use "Claude Official" claude

# 查看详情（API Key 自动脱敏）
"$PYTHON" "$SCRIPT" info MiniMax

# 修复原生订阅失效
"$PYTHON" "$SCRIPT" fix-sub
```

---

## 已配置的 Provider 清单

| App | Provider | 说明 |
|-----|----------|------|
| claude | **Claude Official** ⭐ | 原生订阅，空配置 |
| claude | OfoxAI | `https://api.ofox.ai/anthropic` |
| claude | DeepSeek | `https://api.deepseek.com/anthropic` |
| claude | MiniMax | `https://api.minimaxi.com/anthropic`，M2.7 |
| codex | OfoxAI | Codex 使用，`claude-sonnet-4.6` |
| openclaw | MiniMax M2.5 | `https://api.minimax.io/anthropic` |

---

## fix-sub 操作步骤

当原生 Claude Pro 订阅失效时执行：

```bash
python "06_Python Scripts/06_工具/ccswitch_cli.py" fix-sub
```

该命令执行三步：
1. 切回 DB + settings.json → Claude Official
2. 清除 `~/.claude/settings.json` 中的 `ANTHROPIC_*` env 注入
3. 重置 `~/.claude.json` 中 `hasAvailableSubscription` + 删除 `clientDataCache`

**完成后重启 Claude Code。**

---

## 配置优先级

```
cc-switch 数据库（SSOT）
    ↓ 切换时写入
~/.claude/settings.json（Live 配置）
    ↓ 优先级高于
OAuth Token（~/.claude/.credentials.json）
```

**因此**：只要 `settings.json` 里有 `ANTHROPIC_BASE_URL`，Claude Code 就会走 API Key 模式而非订阅模式。
