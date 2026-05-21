---
name: clash-vpn
description: "Clash VPN 管理工具。用于翻墙、切换节点、管理 VPN 连接。示例：\"打开 VPN\", \"切换节点\", \"翻墙\", \"查看 VPN 状态\", \"导入订阅\""
---

# Clash VPN 管理工具

通过命令行管理 Clash Verge Rev，支持节点切换、订阅导入、状态查看等操作。

## 核心功能

| 功能 | 说明 |
|------|------|
| 打开 VPN | 启动 Clash Verge Rev 应用 |
| 关闭 VPN | 关闭 Clash 应用 |
| 查看状态 | 显示当前连接状态、节点、流量 |
| 切换节点 | 切换到指定代理节点 |
| 切换模式 | 切换代理模式 (rule/global/direct) |
| 列出节点 | 显示所有可用代理节点 |
| 导入订阅 | 导入新的订阅链接 |
| 删除订阅 | 删除已有的订阅 |
| 列出订阅 | 显示所有订阅 |

## 代码位置

- **CLI 工具**: `E:\1.work\douyin\1.shuixing\06_Python Scripts\08_Clash工具\clash_cli.py`
- **Clash Verge Rev 程序**: `C:\Users\Administrator\AppData\Local\io.github.clash-verge-rev.clash-verge-rev\clash-verge.exe`
- **配置目录**: `C:\Users\Administrator\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev`

## 使用方法

### 基本流程

1. **理解用户需求** - 用户需要管理 VPN 时使用
2. **执行对应命令**
3. **返回执行结果**

### 命令语法

```bash
# Python 路径
PYTHON="C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe"

# 查看状态
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" status

# 列出所有节点
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" proxies

# 切换节点 (支持模糊匹配)
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" select "Hong Kong"

# 切换模式
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" mode rule
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" mode global
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" mode direct

# 查看配置
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" config

# 查看日志
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" logs

# 打开 Clash Verge Rev (VPN)
cmd /c "C:\Users\Administrator\AppData\Local\io.github.clash-verge-rev.clash-verge-rev\clash-verge.exe"

# 关闭 Clash Verge Rev
taskkill /f /im "clash-verge.exe"
taskkill /f /im "verge-mihomo.exe"

# 导入订阅
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" import "<订阅URL>" [名称]

# 删除订阅
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" delete "<订阅名称>"

# 列出订阅
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Clash工具/clash_cli.py" profiles
```

## 节点匹配规则

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

## 触发关键词

当用户说以下话时使用此 skill：
- "打开 VPN"
- "关闭 VPN"
- "启动 Clash"
- "翻墙"
- "切换节点"
- "换一个节点"
- "VPN 状态"
- "查看 VPN"
- "代理模式"
- "切换代理"
- "导入订阅"
- "添加订阅"
- "订阅"
- "删除订阅"
- "移除订阅"
- 其他 VPN/翻墙相关操作

## 注意事项

1. **前提条件**: Clash Verge Rev 必须已安装且配置正确
2. **API 依赖**: 状态查询和节点切换依赖 REST API (http://127.0.0.1:9097)
3. **API Secret**: `set-your-secret`
4. **权限**: 部分操作可能需要管理员权限
5. **节点延迟**: 显示的延迟数据仅供参考，实际速度可能不同
6. **订阅导入**: 导入后需重启 Clash Verge Rev 或重新加载配置才能生效

## API 端点

Clash REST API (Mihomo)：
- `GET /proxies` - 获取所有代理节点
- `GET /configs` - 获取当前配置
- `GET /traffic` - 获取实时流量
- `PUT /proxies/GLOBAL` - 切换节点
- `PUT /configs` - 更新配置

## 端口配置

| 端口类型 | 端口号 |
|----------|--------|
| Mixed Port | 7897 |
| SOCKS Port | 7898 |
| HTTP Port | 7899 |
| API Port | 9097 |
