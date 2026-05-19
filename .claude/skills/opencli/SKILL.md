---
name: opencli
description: "使用 OpenCLI 控制浏览器进行网页读取、数据爬取和网站探测。示例：\"帮我读取网页\", \"爬取这个页面\", \"探测这个网站\", \"帮我分析创作者中心\")"
---

# OpenCLI 浏览器自动化工具

通过 Chrome 扩展控制浏览器，读取网页内容、探测网站 API、分析页面数据。

**前提条件**：
1. Chrome 浏览器已安装 OpenCLI 扩展
2. Chrome 中已打开并登录目标网站

## 功能

| 功能 | 命令 | 说明 |
|------|------|------|
| 读取网页 | `opencli web read --url <URL>` | 将网页转为 Markdown |
| 探测网站 | `opencli explore <URL>` | 发现网站 API 和功能 |
| 话题搜索 | `opencli douyin hashtag search --keyword <词>` | 搜索抖音话题热度 |
| AI推荐话题 | `opencli douyin hashtag suggest` | AI 推荐话题 |
| 热点词 | `opencli douyin hashtag hot` | 获取热点词 |
| 诊断连接 | `opencli doctor` | 检查扩展连接状态 |

## 已验证可用的工作流

### 1. 读取抖音创作者中心

```bash
opencli web read --url https://creator.douyin.com
```

可获取：账号信息、粉丝数、获赞数、作品列表摘要、数据概览

### 2. 知乎数据读取

```bash
# 首页信息流（热榜问题）
opencli web read --url https://www.zhihu.com

# 创作中心内容管理
opencli web read --url https://www.zhihu.com/creator/manage/creation
# 可获取：内容列表、阅读/赞同/评论/收藏数据、草稿箱

# 内容分析数据
opencli web read --url https://www.zhihu.com/creator/analytics/work/all
# 可获取：阅读量、播放量、赞同、评论、收藏、分享趋势

# 收益分析
opencli web read --url https://www.zhihu.com/creator/income-analysis
# 可获取：今日/本周/累计收益、创作余额、收益分类

# 搜索内容
opencli web read --url "https://www.zhihu.com/search?type=content&q=关键词"
```

### 3. 小红书数据读取

```bash
# 首页推荐内容
opencli web read --url https://www.xiaohongshu.com

# 搜索内容
opencli web read --url "https://www.xiaohongshu.com/search?keyword=关键词"

# 热门榜单
opencli web read --url https://www.xiaohongshu.com/hot-list

# 话题页
opencli web read --url https://www.xiaohongshu.com/topic
```

注意：小红书创作者平台 (creator.xiaohongshu.com) 需要登录

### 4. wikiHow 知识库读取

```bash
# 首页
opencli web read --url https://www.wikihow.com/Main-Page

# 分类页面（如 Health, Technology, Arts 等）
opencli web read --url https://www.wikihow.com/Category:Health

# 搜索（注意：搜索结果需要登录，可用分类页替代）
opencli web read --url "https://www.wikihow.com/Special:Search?search=关键词"

# 读取具体文章
opencli web read --url https://www.wikihow.com/Use-ChatGPT
```

可获取：文章标题、步骤指南、正文内容、分类信息

### 4. 搜索话题热度

```bash
# 搜索话题
opencli douyin hashtag search --keyword "好书推荐"

# AI 推荐话题
opencli douyin hashtag suggest

# 热点词
opencli douyin hashtag hot
```

### 5. 探测任意网站

```bash
opencli explore https://example.com
```

输出：网站 API 端点列表、能力分析、建议策略

### 6. 检查连接状态

```bash
opencli doctor
```

正常输出：
```
[OK] Daemon: running on port 19825
[OK] Extension: connected
[OK] Connectivity: connected in 0.3s
```

## 已知限制

| 功能 | 状态 | 说明 |
|------|------|------|
| 页面内容读取 | ✅ 正常 | 通过扩展执行 JS 获取页面 |
| 结构化 API 调用 | ⚠️ 不稳定 | 需要登录的 API 可能失败 |
| API 捕获 (record) | ⚠️ 不稳定 | 依赖浏览器拦截 |
| 小红书创作者平台 | ❌ 需要登录 | 需先在浏览器登录 |

## 触发场景

当用户说以下话时使用此 skill：
- "帮我读取网页"
- "爬取这个页面"
- "获取创作者中心信息"
- "分析抖音数据"
- "帮我看看知乎的创作数据"
- "帮我看看小红书的热榜"
- "搜索话题热度"
- "探测这个网站"
- "帮我看看 wikiHow"
- "读取 wikiHow 文章"
- 其他需要浏览器自动化操作的场景

## 知乎内容采集工作流

当用户要求"去知乎搜一下xxx"时，按以下流程执行：

### 1. 搜索
```bash
opencli web read --url "https://www.zhihu.com/search?type=content&q=关键词"
```

### 2. 采集文章
从搜索结果中找到文章链接，逐个读取：
```bash
opencli web read --url "https://zhuanlan.zhihu.com/p/文章ID"
```

### 3. 保存
- 每篇保存到 `00_InBox_收件箱/文章标题/文章标题.md`
- 创建索引：`Claude_Code技巧_索引.md`

### 4. 合并（如用户要求）
用户说"合并成一个MD文件"时：
- **先读所有文章**：用 `Glob` 找所有 `.md` 文件
- **汇总结构**：顶部总结 + 原文按点赞数排列
- **禁止综合**：原文照录，不重新组织

详见记忆文件：`.claude/memory/zhihu内容采集合并工作流.md`

## 注意事项

1. **Chrome 必须运行**：命令通过 Chrome 扩展执行，Chrome 需保持开启
2. **登录状态**：需要登录的网站需在 Chrome 中已登录
3. **等待页面加载**：读取页面时可能需要等待 3-5 秒
4. **临时标签页**：执行时会打开临时标签页，这是正常现象
5. **默认保存原文**：用户未要求合并时，只采集不综合
