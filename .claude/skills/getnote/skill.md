---
name: getnote
description: "调用 Get笔记 (GetNote.fm) API 进行笔记管理、语义搜索。示例：\"创建一条笔记\"、\"搜索笔记\"、\"语义搜索知识库\"、\"查询 getnote 配额\""
---

# Get笔记 API 工具

调用 Get笔记 API 进行笔记管理、语义搜索。

## API 配置

| 配置项 | 值 |
|--------|-----|
| Base URL | `https://openapi.biji.com/open/api/v1` |
| Client ID | `cli_62e1e5fb96c7211b1b02c62e` |
| API Key | `gk_live_87da6636661e7a8f.2a2462e2bb6c3f98e976a4404f96d27254e0f3f7ea634aab` |
| 代理 | `http://127.0.0.1:7890` |

## 脚本位置

`E:/1.work/douyin/1.shuixing/06_Python Scripts/08_Get笔记/getnote_api.py`

## 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `list [limit]` | 获取笔记列表 | `python getnote_api.py list 20` |
| `detail <note_id>` | 获取笔记详情 | `python getnote_api.py detail 1905653611728215960` |
| `create <内容>` | 创建笔记 | `python getnote_api.py create "# 标题\n内容..."` |
| `delete <note_id>` | 删除笔记 | `python getnote_api.py delete <note_id>` |
| `recall <查询>` | 语义召回 | `python getnote_api.py recall "文案风格"` |
| `knowledge` | 获取知识库列表 | `python getnote_api.py knowledge` |
| `bloggers [know_id]` | 获取博主列表 | `python getnote_api.py bloggers qY2BZ56Y` |
| `contents <blog_id>` | 获取博主内容 | `python getnote_api.py contents 1206096` |
| `quota` | 查询配额 | `python getnote_api.py quota` |

## 已知限制

1. **博主内容接口** (`/resource/knowledge/blogger/contents`) 有视频频率限制，建议通过浏览器自动化提取
2. **语义召回** 直接搜索已保存笔记的内容
3. **代理设置** 已内置，无需手动配置

## 语义召回示例

```bash
python getnote_api.py recall "鬼文化"
python getnote_api.py recall "古月安 文案风格"
```

返回匹配笔记的 title、content、note_id 等信息。

## 知识库信息

当前用户已订阅：
- 知识库 ID: `qY2BZ56Y` (对标订阅)
- 博主数量: 22 位（已验证）
- 博主示例: 古月安的宝藏（followId: 1206096）

## 已验证可用接口

| 接口 | 功能 | 状态 |
|------|------|------|
| GET /resource/note/list | 笔记列表 | ✅ |
| POST /resource/recall | 语义召回 | ✅ |
| GET /resource/knowledge/list | 知识库列表 | ✅ |
| GET /resource/knowledge/bloggers | 博主列表 | ✅ |

## 博主内容获取

通过浏览器自动化提取（API接口有频率限制）：
```bash
node extract.js "<完整URL>" "<输出目录>" <最大页数> <最大文章数> <并发数>
```

## 重要说明

1. **博主内容接口** 需要先订阅博主才能获取内容
2. **语义召回** 直接搜索已保存笔记的内容
3. **代理设置** 已内置，无需手动配置
