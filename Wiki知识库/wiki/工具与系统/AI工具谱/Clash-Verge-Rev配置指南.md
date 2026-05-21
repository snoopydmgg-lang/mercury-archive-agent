---
name: Clash-Verge-Rev配置指南
description: Clash Verge Rev VPN 客户端配置与 CLI 管理工具使用指南
type: tool
created: 2026-05-21
updated: 2026-05-21
tags: [VPN, Clash, 代理, 翻墙, Mihomo]
---

# Clash Verge Rev 配置指南

## 概述

Clash Verge Rev 是基于 Mihomo 内核的代理客户端，用于科学上网和网络代理管理。

## 安装信息

| 项目 | 值 |
|------|-----|
| 版本 | v2.5.1 |
| 程序路径 | `C:\Users\Administrator\AppData\Local\io.github.clash-verge-rev.clash-verge-rev\clash-verge.exe` |
| 配置目录 | `C:\Users\Administrator\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev` |
| 核心 | verge-mihomo |

## 端口配置

| 端口类型 | 端口号 | 说明 |
|----------|--------|------|
| Mixed Port | 7897 | 混合代理端口（HTTP+SOCKS） |
| SOCKS Port | 7898 | SOCKS5 代理端口 |
| HTTP Port | 7899 | HTTP 代理端口 |
| API Port | 9097 | REST API 管理端口 |

## API 配置

| 配置项 | 值 |
|--------|-----|
| API 地址 | `http://127.0.0.1:9097` |
| Secret | `set-your-secret` |
| 认证方式 | Bearer Token |

## CLI 工具

项目内置了 Python CLI 工具管理 Clash：

```bash
# Python 路径
PYTHON="C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe"
CLI="$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py"

# 常用命令
$CLI status          # 查看状态
$CLI proxies         # 列出节点
$CLI select "US"     # 切换到美国节点
$CLI mode rule       # 规则模式
$CLI mode global     # 全局代理
$CLI profiles        # 列出订阅
```

## 节点匹配

支持模糊匹配，大小写不敏感：

| 关键词 | 匹配示例 |
|--------|----------|
| `hk`, `hong`, `香港` | Hong Kong 01, HK 06 |
| `sg`, `singapore`, `新加坡` | Singapore 01, SG 06 |
| `jp`, `japan`, `日本` | Japan 01, JP 06 |
| `us`, `美国` | US 01, US 06 |
| `tw`, `taipei`, `台湾` | Taipei 01 |

## 代理模式

| 模式 | 说明 |
|------|------|
| `rule` | 规则模式（推荐，默认） |
| `global` | 全局代理 |
| `direct` | 直连（不使用代理） |

## 环境变量代理

当 GitHub 等服务不可达时，设置代理环境变量：

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7897"
$env:HTTPS_PROXY="http://127.0.0.1:7897"
```

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| API 连接失败 | 检查 Clash Verge Rev 是否运行，端口 9097 是否被占用 |
| 节点切换无效 | 重启 Clash Verge Rev 或重新加载配置 |
| 代理不生效 | 检查系统代理设置是否开启 |
| NotebookLM 不可用 | 确保使用美国节点，且 Google 账号地区设置为 US |

## 相关链接

- GitHub: https://github.com/clash-verge-rev/clash-verge-rev
- Mihomo: https://github.com/MetaCubeX/mihomo
