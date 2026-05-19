---
name: everything
description: "Everything 文件搜索工具。用于快速搜索文件名、按照扩展名搜索、查找文件路径。示例：\"搜索文件\", \"找一下 xxx\", \"按扩展名搜索\", \"查看 PDF 文件\""
---

# Everything CLI 工具

通过命令行快速搜索文件，利用 Everything 的全文索引实现毫秒级搜索。

## 数据位置

- **Everything 程序**: `D:\Everything\Everything.exe`
- **HTTP API**: `http://127.0.0.1:80`

## 核心功能

| 功能 | 说明 |
|------|------|
| 快速搜索 | 按文件名搜索 |
| 扩展名搜索 | 按文件扩展名搜索 |
| 路径搜索 | 在指定路径下搜索 |
| 状态检查 | 检查 HTTP API 是否可用 |

## 代码位置

`E:\1.work\douyin\1.shuixing\06_Python Scripts\10_Everything工具\everything_cli.py`

## 使用方法

### 基本流程

1. **理解用户需求** - 用户需要搜索文件时使用
2. **执行对应命令**
3. **返回执行结果**

### 命令语法

```bash
# Python 路径
PYTHON="C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe"

# 搜索文件（按文件名）
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/10_Everything工具/everything_cli.py" search "关键词"
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/10_Everything工具/everything_cli.py" s "关键词"

# 搜索文件（限制结果数）
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/10_Everything工具/everything_cli.py" search "关键词" -n 20

# 按扩展名搜索
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/10_Everything工具/everything_cli.py" ext pdf
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/10_Everything工具/everything_cli.py" ext docx

# 在指定路径下搜索
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/10_Everything工具/everything_cli.py" path "D:/项目" "关键词"

# 检查状态
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/10_Everything工具/everything_cli.py" status

# 打开 Everything 窗口
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/10_Everything工具/everything_cli.py" open
```

## Everything 搜索语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `*.ext` | 按扩展名搜索 | `*.txt`, `*.pdf` |
| `keyword` | 包含关键词 | `report` |
| `"exact name"` | 精确搜索 | `"my document"` |
| `ext:doc` | 指定扩展名 | `ext:doc` |
| `size:>1mb` | 大于指定大小 | `size:>1mb` |
| `date:2024-01-01` | 指定日期 | `date:2024-01-01` |
| `regex:^a.*\.pdf$` | 正则表达式 | `regex:^a.*\.pdf$` |

## 搜索选项

| 选项 | 说明 |
|------|------|
| `-n, --max <数量>` | 最大结果数（默认50） |
| `--no-path` | 不显示完整路径 |
| `--no-size` | 不显示文件大小 |

## 触发关键词

当用户说以下话时使用此 skill：
- "搜索文件"
- "找一下"
- "查找"
- "帮我找"
- "按扩展名搜索"
- "查看 PDF"
- "找 txt 文件"
- "搜索 xxx"
- 其他文件搜索相关操作

## 注意事项

1. **HTTP API**: Everything 需要启用 HTTP 服务器才能使用 CLI 后台搜索
   - 启用方法: Everything → 设置 → HTTP服务器 → 启用HTTP服务器
2. **首次启用需要重启**: 修改配置后需要重启 Everything
3. **管理员权限**: 搜索系统文件可能需要管理员权限
4. **索引更新**: Everything 自动索引文件变化，实时更新

## 数据结构

搜索结果返回:
```json
{
  "name": "文件名.txt",
  "path": "C:\\Users\\...\\路径",
  "size": 2048
}
```
