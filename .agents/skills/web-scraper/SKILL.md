---
name: web-scraper
description: "Use when user provides URLs and asks to scrape data from them, or clean/parse web content. Examples: \"帮我爬取这个网页\", \"抓取这个链接的数据\", \"清洗网页内容\""
---

# 网页数据爬取工作流

从网页URL爬取数据并清洗。

## 功能

| 功能 | 说明 |
|------|------|
| 网页爬取 | 使用 Playwright 抓取网页内容 |
| HTML清洗 | 移除无用标签（nav, footer, script, style, aside） |
| 内容提取 | 提取核心内容区（main, article, body） |
| 格式转换 | 将HTML转换为Markdown格式 |

## 代码位置

`E:\1.work\douyin\1.shuixing\06_Python Scripts\scraper.py`

## 使用方法

### 1. 用户提供URL时

当用户提供URL链接时：

1. **获取URL列表** - 从用户消息中提取URL
2. **运行爬虫脚本**:
   ```bash
   cd "E:/1.work/douyin/1.shuixing/06_Python Scripts"
   python scraper.py
   ```
3. **输入URL** - 脚本会提示输入URL，多个URL用逗号分隔
4. **等待完成** - 数据会保存到 `Claude_Code_Manual.md`

### 2. 直接指定URL

也可以在运行时直接修改代码中的URL列表，或通过命令行参数传入。

## 依赖安装

首次使用需要安装依赖：
```bash
pip install playwright beautifulsoup4 markdownify
playwright install chromium
```

## 输出

- 爬取的内容保存为 Markdown 格式
- 文件名：`Claude_Code_Manual.md`（当前代码默认文件名）

## 注意事项

1. **URL格式**：确保URL以 http:// 或 https:// 开头
2. **多个URL**：用逗号分隔，如：`url1, url2, url3`
3. **随机延迟**：请求之间有2秒延迟，避免被封禁
4. **重试机制**：最多重试3次

## 常用URL示例

如果用户没有提供具体URL，可以询问用户需要爬取什么网站的内容。

## 数据清洗规则

当前代码的清洗规则：
- 移除 `nav`, `footer`, `script`, `style`, `aside` 标签
- 优先提取 `class="prose"` 或 `class="article"` 的 div
- 如果没有，则提取 `main` 或 `body`

如需针对特定网站调整清洗规则，可以修改代码。
