---
title: C盘空间清理与根本治理方案
录入日期: 2026-05-14
---

## 根因分析

Windows 应用程序数据堆积在 C 盘的根本原因：

1. **系统环境变量默认指向** — `%APPDATA%` 和 `%LOCALAPPDATA%` 硬编码在 `C:\Users\<Username>\AppData`
2. **应用开发规范缺失** — 多数应用（剪映、微信、Electron 应用）硬编码缓存路径，UI 不提供数据位置选项
3. **开发工具链默认行为** — npm、pip、playwright 等默认将全局包和缓存下载至用户目录

## 三层治理方案

### 层级一：开发工具链缓存迁移 (CLI)

```powershell
$targetDir = "D:\DevCache"
New-Item -ItemType Directory -Force -Path "$targetDir\npm"
New-Item -ItemType Directory -Force -Path "$targetDir\pip"
New-Item -ItemType Directory -Force -Path "$targetDir\playwright"
New-Item -ItemType Directory -Force -Path "$targetDir\electron-builder"

npm config set cache "$targetDir\npm"
pip config set global.cache-dir "$targetDir\pip"
[Environment]::SetEnvironmentVariable("PLAYWRIGHT_BROWSERS_PATH", "$targetDir\playwright", "User")
[Environment]::SetEnvironmentVariable("ELECTRON_BUILDER_CACHE", "$targetDir\electron-builder", "User")
```

### 层级二：NTFS 目录联接 (Junction)

对于无法修改缓存路径的应用，使用 `mklink /J` 在文件系统层重定向，对应用完全透明。

```powershell
$source = "$env:APPDATA\<应用名>"
$destination = "D:\AppData_Roaming\<应用名>"
New-Item -ItemType Directory -Force -Path "D:\AppData_Roaming" | Out-Null
Move-Item -Path $source -Destination $destination -Force
cmd /c mklink /J "$source" "$destination"
```

**已迁移清单 (2026-05-14):**

| 应用 | 源路径 | 目标路径 | 释放 |
|------|--------|----------|------|
| 酷狗音乐 | `%APPDATA%\KuGou8` | `D:\AppData_Roaming\KuGou8` | 1.95 GB |
| 必剪 | `%LOCALAPPDATA%\BCUT` | `D:\AppData_Local\BCUT` | 2.08 GB |
| 必剪 | `%APPDATA%\BCUT` | `D:\AppData_Roaming\BCUT` | 1.04 GB |
| 夸克浏览器 | `%LOCALAPPDATA%\Quark` | `D:\AppData_Local\Quark` | 2.1 GB |

### 层级三：应用原生迁移

部分应用大版本更新可能使 Junction 失效，需使用原生功能：

| 应用 | 操作 | 预期释放 |
|------|------|----------|
| 微信 | 左下角菜单 → 设置 → 文件管理 → 更改 → 选 D 盘 | ~5.7 GB |
| 剪映专业版 | 全局设置 → 草稿位置更改 → 缓存管理清空并改路径 | ~10.9 GB |
| OneDrive | 任务栏图标 → 设置 → 账户 → 取消链接 → 重新登录选新位置 | ~12.9 GB |

## 自动化空间回收

```powershell
# cleanup.ps1 — 任务计划程序每周执行
$pathsToClean = @(
    "$env:LOCALAPPDATA\Temp\*",
    "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache\Cache_Data\*",
    "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache\Cache_Data\*"
)
foreach ($path in $pathsToClean) {
    if (Test-Path (Split-Path $path)) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}
```

## 执行记录

| 日期 | 操作 | 释放空间 | 累计释放 |
|------|------|----------|----------|
| 2026-05-13 | Ditto 数据库清理 | ~20 GB | 20 GB |
| 2026-05-13 | uv cache clean | 3.2 GB | 23.2 GB |
| 2026-05-13 | pip cache purge | ~0.85 GB | 24 GB |
| 2026-05-14 | 飞书 LarkShell\aha 删除 | 7.26 GB | 31.3 GB |
| 2026-05-14 | 层级一：dev 工具链重定向 | - | - |
| 2026-05-14 | electron-builder 旧缓存删除 | 1.27 GB | 32.6 GB |
| 2026-05-14 | ms-playwright 旧缓存删除 | 1.19 GB | 33.8 GB |
| 2026-05-14 | 层级二：4个 Junction 迁移 | 7.17 GB | 40.9 GB |

**总释放: ~41 GB | C 盘使用率: 81% → 69%**
