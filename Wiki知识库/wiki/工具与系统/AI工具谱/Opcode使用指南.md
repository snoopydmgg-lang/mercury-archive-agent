---
title: Opcode 使用与维护指南
aliases:
  - "Opcode使用"
  - "Opcode指南"
tags:
  - 工具与系统
关联笔记: []
录入日期: 2026-04-21
---

# Opcode 使用与维护指南

> Claude Code 的 GUI 指挥中心 -- 可视化管理会话、智能体、MCP 服务器、用量分析
> 项目地址: https://github.com/winfunc/opcode (原 getAsterisk/opcode)
> 本地代码: `06_Python Scripts/08_Opcode/`
> 版本: v0.2.1 | 技术栈: Tauri 2 + React 18 + TypeScript + Rust

---

## 🔧 最新修复（2026-04-14）

已修复三个核心问题，需重新构建生效：

| 问题 | 状态 | 修复位置 |
|------|------|----------|
| ✅ 中文界面不显示 | 已修复 | `src/main.tsx` 第 10 行添加 i18n 导入 |
| ✅ 终端窗口闪现 | 已修复 | `src-tauri/src/commands/claude.rs` 添加 CREATE_NO_WINDOW |
| ✅ 发消息弹终端 | 已修复 | 同上（进程创建统一修复） |

**重新构建命令：**
```powershell
cd "E:\1.work\douyin\1.shuixing\06_Python Scripts\08_Opcode"
bun install
bun run tauri build
```

构建完成后运行 `src-tauri/target/release/opcode.exe`

---

## 一、Opcode 是什么

Opcode 是一个桌面 GUI 应用，把 Claude Code CLI 包装成可视化界面。核心能力:

| 模块 | 能力 | 对应 CLI 操作 |
|------|------|--------------|
| 项目管理 | 浏览 `~/.claude/projects/`，查看/恢复会话 | `claude --resume` |
| CC 智能体 | 创建自定义 Agent，后台执行，执行历史 | `claude -p "..." --model` |
| 用量仪表板 | 按模型/项目/时段的 Token 和成本分析 | 手动算 |
| MCP 管理 | 图形化添加/测试/导入 MCP 服务器 | 编辑 settings.json |
| 时间线/检查点 | 会话版本控制，分支，Diff 对比 | git stash 类比 |
| CLAUDE.md 编辑 | 内置 Markdown 编辑器+实时预览 | 手动编辑 |
| Web 模式 | 手机/浏览器远程访问（实验性） | 无 |

---

## 二、安装（Windows）

### 前置依赖

```
1. Claude Code CLI   -- npm install -g @anthropic-ai/claude-code
2. Rust 1.70+        -- https://rustup.rs
3. Bun (最新版)       -- https://bun.sh
4. Git               -- https://git-scm.com
5. MSVC 构建工具      -- Visual Studio Build Tools (C++ 桌面开发)
6. WebView2           -- Windows 11 自带，Win10 需手动安装
```

### 构建步骤

```powershell
# 1. 克隆（已克隆到 06_Python Scripts/08_Opcode/）
cd "E:\1.work\douyin\1.shuixing\06_Python Scripts\08_Opcode"

# 2. 安装前端依赖
bun install

# 3. 开发模式（带热更新）
bun run tauri dev

# 4. 生产构建
bun run tauri build
# 产物位置: src-tauri/target/release/opcode.exe
# 安装包: src-tauri/target/release/bundle/ (.msi / .exe)
```

### 构建常见问题

| 报错 | 原因 | 解决 |
|------|------|------|
| `cargo not found` | Rust 未装或不在 PATH | 装 rustup，重启终端 |
| `MSVC not found` | 缺 C++ 构建工具 | 装 VS Build Tools，勾选 C++ |
| `claude command not found` | CLI 未装或不在 PATH | `npm i -g @anthropic-ai/claude-code`，验证 `claude --version` |
| `out of memory` | 内存不足 | `cargo build -j 2` 限制并行数 |
| `WebView2 not found` | Win10 缺 WebView2 | 去微软官网下载安装 |

---

## 三、中文界面设置

Opcode 内置中文支持（`zh-CN`），已有完整翻译文件。

### 语言检测机制

```
优先级: localStorage > 浏览器语言 > 英语(fallback)
```

配置文件: `src/lib/i18n.ts`
```typescript
detection: {
  order: ['localStorage', 'navigator'],  // 先查本地存储，再查浏览器语言
  caches: ['localStorage'],               // 缓存到 localStorage
},
```

### ✅ 已修复：中文界面不显示问题

**问题原因：** i18n 未在 `main.tsx` 中初始化导入

**修复方案：** 已在 `src/main.tsx` 第 10 行添加：
```typescript
import "./lib/i18n"; // Initialize i18n
```

重新构建后中文界面将自动生效（根据系统语言自动检测）。

### 如果界面仍显示英文

**方案 1: 检查系统语言**
- Windows 设置 > 时间和语言 > 语言 > 首选语言 > 确保中文在列表中

**方案 2: 手动切换（开发者工具）**
1. 打开 Opcode
2. 按 `F12` 打开开发者工具
3. 在 Console 输入:
```javascript
localStorage.setItem('i18nextLng', 'zh-CN');
location.reload();
```

**方案 3: 修改默认语言（改代码）**
编辑 `src/lib/i18n.ts`:
```typescript
// 把 fallbackLng 改为中文
fallbackLng: 'zh-CN',
```
然后重新构建。

### 翻译文件位置

| 语言 | 文件 |
|------|------|
| 英文 | `src/locales/en.json` |
| 中文 | `src/locales/zh-CN.json` |

中文翻译已覆盖全部模块: 设置、项目、会话、智能体、用量、MCP、时间线、检查点、存储等。

---

## 四、核心功能使用

### 4.1 项目管理

```
欢迎页 > 项目 > 选择项目 > 查看会话 > 恢复/新建
```

- 自动扫描 `~/.claude/projects/` 下的所有项目
- 每个会话显示: 首条消息、时间戳、Token 用量
- 支持搜索、按名称/日期/活动排序
- 右键菜单: 在编辑器中打开、在文件管理器中显示

### 4.2 CC 智能体

```
欢迎页 > CC 智能体 > 创建智能体 > 配置 > 执行
```

**创建步骤:**
1. 设置名称、图标、系统提示词
2. 选择模型（Sonnet / Opus）
3. 配置权限（文件读写、网络访问）
4. 选择目标项目，运行

**内置模板:**
- 代码审查员、Bug 修复器、文档编写器
- 测试生成器、重构器、安全审计员、性能优化器

**预置智能体（本地已有）:**

| 智能体 | 文件 | 用途 |
|--------|------|------|
| Git Commit Bot | `cc_agents/git-commit-bot.opcode.json` | 自动分析 diff + 写 commit message + push |
| Security Scanner | `cc_agents/security-scanner.opcode.json` | 安全扫描 |
| Unit Tests Bot | `cc_agents/unit-tests-bot.opcode.json` | 自动生成单元测试 |

**导入智能体:** 直接把 `.opcode.json` 文件放到 `cc_agents/` 目录

### 4.3 用量仪表板

```
菜单 > 使用仪表板 > 查看分析
```

- 按模型/项目/时段查看 Token 消耗和成本
- 可视化图表显示趋势
- 支持导出 CSV / JSON
- 区分: 输入 Token、输出 Token、缓存创建、缓存读取

### 4.4 MCP 服务器管理

```
菜单 > MCP 服务器 > 添加服务器 > 配置
```

- 手动添加或通过 JSON 导入
- 从 Claude Desktop 导入配置
- 连接测试确认可用性
- 查看每个服务器提供的工具和资源

### 4.5 时间线与检查点

```
项目 > 时间线 > 创建检查点 / 恢复检查点
```

**检查点策略（在设置中配置）:**
- 仅手动: 只在你主动创建时保存
- 每次提示后: 每轮对话后自动保存
- 工具使用后: 每次 Agent 调用工具后保存
- 智能（推荐）: 自动判断最佳时机

**注意:** 检查点功能标记为"实验性"，可能影响目录结构或导致数据丢失，谨慎使用。

### 4.6 CLAUDE.md 编辑

```
项目 > CLAUDE.md > 编辑
```

- 内置 Markdown 编辑器 + 语法高亮
- 实时预览渲染效果
- 自动扫描项目中所有 CLAUDE.md 文件

### 4.7 Web 模式（实验性）

通过 Web Server 从手机/浏览器访问 Claude Code:

```powershell
# 启动 Web 服务
cd "E:\1.work\douyin\1.shuixing\06_Python Scripts\08_Opcode"
cd src-tauri && cargo run --bin opcode-web

# 自定义端口
cd src-tauri && cargo run --bin opcode-web -- --port 3000
```

访问: `http://你的IP:8080`

**已知限制（当前版本）:**
- 仅适合单会话使用，多会话会互相干扰
- 取消按钮不起作用（进程未实际终止）
- stderr 错误信息不显示
- 安全性: 使用了 `--dangerously-skip-permissions`，仅限局域网使用

---

## 五、设置详解

### 5.1 代理配置（翻墙）

设置 > 代理:
- HTTP 代理: `http://127.0.0.1:7890`
- HTTPS 代理: `http://127.0.0.1:7890`
- 无代理: `localhost,127.0.0.1`

### 5.2 Claude 二进制路径

设置 > 高级 > Claude 二进制路径:
- 自动检测: 点击"自动检测"按钮
- 手动指定: 输入 claude.exe 的完整路径
- 验证: 点击"验证"确认路径有效

### 5.3 权限规则

设置 > 权限:
- 允许/拒绝特定工具（Bash、Read、Write、Edit）
- 配置通配符模式

### 5.4 环境变量

设置 > 环境:
- 添加 API 密钥（加密存储）
- 设置自定义环境变量

### 5.5 数据库管理

设置 > 存储:
- 查看内置 SQLite 数据库
- SQL 查询编辑器（直接执行查询）
- 重置数据库（清空所有数据重建）

---

## 六、常见问题排查

### ✅ 已修复：终端窗口闪现问题（完整方案）

**问题描述：** Windows 下使用 Opcode 时，每次发送消息或执行操作都会弹出黑色终端窗口一闪而过

**问题原因：** Rust 后端启动 Claude 进程时未设置 Windows 的 `CREATE_NO_WINDOW` 标志

**完整修复方案（需修改 5 个文件）：**

#### 1. `src-tauri/src/claude_binary.rs`
```rust
// 在文件开头添加 Windows 导入
#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

// 在 create_command_with_env 函数末尾添加（第625行附近）
#[cfg(target_os = "windows")]
{
    const CREATE_NO_WINDOW: u32 = 0x08000000;
    cmd.creation_flags(CREATE_NO_WINDOW);
}
```

#### 2. `src-tauri/src/commands/claude.rs`
```rust
// 在文件开头添加 Windows 导入（第1行附近）
#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

// 在 create_command_with_env 函数末尾添加（第289行附近）
#[cfg(target_os = "windows")]
{
    const CREATE_NO_WINDOW: u32 = 0x08000000;
    tokio_cmd.creation_flags(CREATE_NO_WINDOW);
}
```

#### 3. `src-tauri/src/commands/agents.rs`
```rust
// 在文件开头添加 Windows 导入（第16行附近）
#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

// 在 create_command_with_env 函数末尾添加（第1700行附近）
#[cfg(target_os = "windows")]
{
    const CREATE_NO_WINDOW: u32 = 0x08000000;
    tokio_cmd.creation_flags(CREATE_NO_WINDOW);
}
```

#### 4. `src-tauri/src/web_server.rs`
```rust
// 在文件开头添加 Windows 导入（第20行附近）
#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

// 在三个 Command::new 调用后添加（第485行、第607行、第701行附近）
// 每个位置都要添加：
#[cfg(target_os = "windows")]
{
    const CREATE_NO_WINDOW: u32 = 0x08000000;
    cmd.creation_flags(CREATE_NO_WINDOW);
}
```

**重新编译：**
```powershell
cd "E:\1.work\douyin\1.shuixing\06_Python Scripts\08_Opcode"
# 关闭正在运行的 Opcode
taskkill /F /IM opcode.exe

# 重新编译
cd src-tauri
cargo build --release --bin opcode

# 启动新版本
cd target/release
start opcode.exe
```

编译完成后，终端窗口将不再闪现。

---

### Q1: 启动后白屏

**原因:** 前端构建失败或 WebView2 缺失
**排查:**
```powershell
# 检查前端是否构建成功
ls dist/

# 重新构建前端
bun run build

# 检查 WebView2
# Win11 自带，Win10 需去微软官网下载
```

### Q2: "Failed to load projects" 加载项目失败

**原因:** `~/.claude` 目录不存在或权限问题
**排查:**
```powershell
# 检查目录
ls $env:USERPROFILE\.claude\projects\

# 如果不存在，先运行一次 Claude Code CLI
claude --version
```

### Q3: 智能体运行卡住

**原因:** Claude 二进制路径未配置或网络问题
**排查:**
1. 设置 > 高级 > 验证 Claude 二进制路径
2. 检查代理设置是否正确
3. 终端测试: `claude --version`

### Q4: 界面文字显示乱码/方框

**原因:** 字体缺失
**排查:** 确保系统安装了中文字体（微软雅黑等）

### Q5: 构建时间过长

**提速方法:**
```powershell
# Debug 构建（更快但产物更大）
bun run tauri build --debug

# 限制并行编译
$env:CARGO_BUILD_JOBS = "2"
bun run tauri build
```

### Q6: MCP 服务器连接失败

**排查:**
1. 确认 MCP 服务器进程已启动
2. 检查服务器命令和参数是否正确
3. 使用内置"连接测试"功能验证

---

## 七、维护与更新

### 更新 Opcode

```powershell
cd "E:\1.work\douyin\1.shuixing\06_Python Scripts\08_Opcode"

# 拉取最新代码
git pull origin main

# 更新依赖
bun install

# 重新构建
bun run tauri build
```

### 清理构建缓存

```powershell
# 清理全部
bun run clean   # 如果 justfile 有定义
# 或手动
rm -rf node_modules dist
cd src-tauri && cargo clean
```

### 数据位置

| 数据 | 路径 |
|------|------|
| 项目和会话 | `~/.claude/projects/` |
| 设置 | `~/.claude/settings.json` |
| Opcode 数据库 | 应用内 SQLite |
| 智能体配置 | `cc_agents/*.opcode.json` |
| 语言设置 | 浏览器 localStorage (`i18nextLng`) |

### 备份建议

- 定期备份 `cc_agents/` 目录（自定义智能体）
- `~/.claude/` 目录包含所有会话历史

---

## 八、使用技巧

### 技巧 1: 快速切换中英文
```javascript
// 在开发者工具 Console 中
// 切中文
localStorage.setItem('i18nextLng', 'zh-CN'); location.reload();
// 切英文
localStorage.setItem('i18nextLng', 'en'); location.reload();
```

### 技巧 2: 导出智能体配置分享
智能体配置存储为 `.opcode.json` 文件，可以直接复制给别人用:
```
cc_agents/git-commit-bot.opcode.json  -- 复制这个文件即可分享
```

### 技巧 3: 用 SQL 查询分析使用模式
设置 > 存储 > SQL 查询编辑器:
```sql
-- 查看所有智能体
SELECT * FROM agents;

-- 查看运行历史
SELECT * FROM agent_runs ORDER BY created_at DESC LIMIT 20;
```

### 技巧 4: Web 模式手机远程用
适合出门在外临时用手机操作 Claude Code:
```powershell
# PC 端启动
cd src-tauri && cargo run --bin opcode-web
# 手机浏览器访问 http://你的局域网IP:8080
```

### 技巧 5: 配合 cc-switch 使用
切换 Provider 后，Opcode 的模型选择会跟随 Claude Code CLI 的配置:
```powershell
# 切到官方 Pro
ccswitch fix-sub
# 然后在 Opcode 中选择 Opus / Sonnet
```

---

## 九、架构速览（开发者参考）

```
opcode/
+-- src/                    # React 前端
|   +-- components/         # UI 组件（Settings, ClaudeCodeSession 等）
|   +-- lib/                # 工具库（i18n, apiAdapter, analytics）
|   +-- locales/            # 国际化（en.json, zh-CN.json）
|   +-- stores/             # Zustand 状态管理
|   +-- hooks/              # React Hooks
+-- src-tauri/              # Rust 后端
|   +-- src/
|   |   +-- commands/       # Tauri 命令处理器
|   |   +-- checkpoint/     # 检查点管理
|   |   +-- process/        # 进程管理
|   |   +-- web_server.rs   # Web 模式服务器
|   +-- tests/              # Rust 测试
+-- cc_agents/              # 预置智能体配置
+-- dist/                   # 前端构建产物
```

技术栈:
- 前端: React 18 + TypeScript + Vite 6 + Tailwind CSS v4 + shadcn/ui
- 后端: Rust + Tauri 2 + SQLite
- 包管理: Bun
- 国际化: i18next + react-i18next
- 动画: Framer Motion

---

*最后更新: 2026-04-14*
*萃取自: raw/AI学习/winfuncopcode... + 本地 08_Opcode 源码分析*
