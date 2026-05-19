---
name: cli-anything
description: "为任意 GUI 软件构建 CLI 工具。示例：\"为 GIMP 创建命令行工具\", \"给 Blender 添加 CLI\", \"生成软件自动化工具\""
---

# CLI-Anything

为任意 GUI 应用程序构建完整的、有状态的 CLI 工具。

## 核心功能

| 功能 | 说明 |
|------|------|
| GUI 分析 | 分析软件源码和架构 |
| CLI 构建 | 自动生成 Click-based CLI |
| 状态管理 | 支持 REPL 模式 |
| 批量操作 | 支持脚本化批量处理 |

## 使用方式

```
/cli-anything <软件路径或GitHub仓库URL>
```

**参数**：
- `<软件路径>` - 本地源码路径（如 `./blender`）
- `<仓库URL>` - GitHub 仓库 URL（如 `https://github.com/GNOME/gimp`）

## 工作流程

### Phase 1: 源码分析
- 分析后端引擎和数据模型
- 映射 GUI 操作到 API 调用
- 识别现有 CLI 工具

### Phase 2: 架构设计
- 设计命令组
- 规划状态模型
- 创建 SOP 文档

### Phase 3: 实现
- 创建 `agent-harness/cli_anything/<software>/` 目录结构
- 实现核心模块（project, session, export 等）
- 构建 Click CLI + REPL 支持

### Phase 4: 测试
- 单元测试 + E2E 测试
- `--json` 输出模式验证
- 路径无关的 subprocess 测试

## 示例

```bash
# 从本地源码构建
/cli-anything /home/user/gimp

# 从 GitHub 仓库构建
/cli-anything https://github.com/blender/blender
```

## 触发场景

当用户说以下话时使用此 skill：
- "为 XXX 创建 CLI"
- "给 XXX 添加命令行工具"
- "生成 XXX 的自动化工具"
- "构建 XXX 的 CLI"
- 其他需要为软件生成 CLI 工具的场景

## 注意事项

1. **源码必须存在**：CLI-Anything 需要分析软件源码
2. **不支持纯二进制**：需要有源码才能分析
3. **需要 Python 环境**：生成的 CLI 基于 Click 框架
4. **可能需要安装依赖**：构建后需要 `pip install -e .`
