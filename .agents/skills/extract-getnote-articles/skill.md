---
name: extract-getnote-articles
description: "自动提取 Get笔记 知识库中博主的所有短视频文案。示例：\"提取这个知识库的文章 https://www.biji.com/subject/ABC123\"、\"帮我爬取这个博主的文案\"、\"把 getnote 知识库的内容导出\""
---

# Get笔记 文案提取工具

自动提取 Get笔记 知识库中的所有文章，保存为 Markdown 文件。

## 功能特点

- 并行提取：3个并发，速度约 25-30 篇/分钟
- 格式化输出：保存为结构化的 Markdown 文件
- 断点续传：自动跳过已提取的文章
- 智能命名：使用博主名称命名文件夹

## 依赖

- **工具位置**：`C:/Users/Administrator/.Codex/skills/extract-getnote-articles/`
- **Node.js** 运行环境
- **Playwright** 浏览器自动化
- **Edge 浏览器**（已配置使用 Edge 的用户数据）

## 使用方法

### 前提条件

1. 关闭所有 Edge 浏览器窗口
2. 确保在 getnote 网页端已登录订阅目标博主

### 运行提取

```bash
cd "C:/Users/Administrator/.Codex/skills/extract-getnote-articles"
node extract.js "<完整URL>" "<输出目录>" <最大页数> <最大文章数> <并发数>
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 完整URL | 知识库URL，必须包含 followName | 必填 |
| 输出目录 | 相对路径 | 必填 |
| 最大页数 | 0=全部 | 0 |
| 最大文章数 | 0=全部 | 0 |
| 并发数 | 默认3，建议不超过5 | 3 |

### 示例

```bash
# 提取古月安的宝藏（完整URL）
node extract.js "https://www.biji.com/subject/qY2BZ56Y/DEFAULT?followId=1206096&followName=%E5%8F%A4%E6%9C%88%E5%AE%89%E7%9A%84%E5%AE%9D%E8%97%8F" "E:/1.work/douyin/1.shuixing/古月安的宝藏" 0 0 3

# 简写（只需知识库ID）
node extract.js "oJOKRwOJ" "输出目录" 0 0 3
```

## 输出

文章保存在指定目录，以博主名称命名的文件夹中。每篇文章为独立的 .md 文件。

## 浏览器配置

已修改为使用 Edge 浏览器用户数据：
- Edge 路径：`C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`
- 用户数据：`C:/Users/Administrator/AppData/Local/Microsoft/Edge/User Data`

## API 信息

getnote API（新版）已可访问：
- Base URL: `https://openapi.biji.com/open/api/v1`
- Client ID: `cli_62e1e5fb96c7211b1b02c62e`
- API Key: `gk_live_87da6636661e7a8f.2a2462e2bb6c3f98e976a4404f96d27254e0f3f7ea634aab`

### 可用 API 命令

```bash
# 查看笔记列表
python "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/getnote_api.py" list 20

# 语义搜索
python "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/getnote_api.py" recall "关键词"

# 查看知识库
python "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/getnote_api.py" knowledge

# 查看博主列表（知识库 qY2BZ56Y 有 22 位博主）
python "E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/getnote_api.py" bloggers qY2BZ56Y
```
