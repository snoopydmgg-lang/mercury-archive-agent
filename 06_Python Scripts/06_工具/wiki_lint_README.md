# Wiki Lint Tool v2.1 使用指南

## 概述

**wiki_lint.py** 是针对抖音创作知识库（`03_Assets_全局库/`）的自动化健康检查脚本。

基于 SCHEMA.md 规则，覆盖 **11 个维度**的完整性检查，生成清晰的问题清单。

---

## 快速使用

```bash
# Windows（完整 Python 路径）
"C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" \
  "E:/1.work/douyin/1.shuixing/06_Python Scripts/06_工具/wiki_lint.py"

# 输出：详细的问题报告 + 总问题数
# Exit code: 0（无问题）/ 1（有问题）
```

---

## 检查维度

| # | 检查项 | 对应规则 | 优先级 |
|----|--------|----------|--------|
| [1] | **死链检测** | wiki/ 中的链接（双链 + Markdown）是否可达 | 🟠 |
| [2] | **孤立页面** | wiki/ 下有页面没有被任何文件引用 | 🟠 |
| [3a] | **Dead References** | index.md 引用的文件在磁盘上找不到 | 🔴 |
| [3b] | **Missing Index** | wiki/ 下的文件没有在 index.md 中列出 | 🟡 |
| [3c] | **Missing Dirs** | index.md 列出的子目录在磁盘上不存在 | 🟡 |
| [4] | **Non-MD Files** | wiki/ 中不是 .md 格式的文件 | 🟢 |
| [5] | **Raw Root Files** | raw/ 根目录直接放置文件（应只有子目录） | 🟢 |
| [6] | **Raw Naming** | raw/ 文件名不符合 `YYYYMMDD_` 前缀规范 | 🟡 |
| [7] | **Frontmatter** | wiki/ 文件缺少必填 frontmatter 字段（title、录入日期） | 🟡 |
| [8] | **No Outbound Links** | wiki/ 页面没有指向其他 wiki 页面的链接（孤岛） | 🟡 |
| [9] | **Unextracted Files** | raw/ 有文件但 wiki/ 没有对应的萃取页面 | ℹ️ |
| [10] | **log.md Integrity** | log.md 中的行不符合操作日志格式 | 🟢 |
| [11a] | **Index/Log Mix** | index.md 中混入了操作日志行 | 🟢 |
| [11b] | **Index/Log Mix** | log.md 中混入了目录索引链接 | 🟢 |
| [+] | **Unknown Dirs** | wiki/ 中出现不在白名单的一级子目录 | 🟢 |

### 优先级说明
- 🔴 **Critical**: 必须立即修复，否则知识库无法正常索引
- 🟠 **High**: 影响知识库可用性，需优先处理
- 🟡 **Medium**: 影响知识库规范性，应在迭代中改进
- 🟢 **Low**: 监控即可，一般不需立即修复
- ℹ️ **Info**: 正常状态，作为持续改进的清单

---

## 输出格式

```
WIKI LINT REPORT  —  2026-04-13 21:18
============================================================
  wiki/ 路径: E:\...\03_Assets_全局库\wiki
  wiki/ 文件数: 14
  raw/  文件数: 130

────────────────────────────────────────────────────────────
  [1] 死链  (62 项)
────────────────────────────────────────────────────────────
  DEAD  AI工具谱/cc-switch使用指南.md  →  [[Claude账号安全]]
  DEAD  个人成长/README.md  →  [[20260411_有限理性]]
  ...

────────────────────────────────────────────────────────────
  [2] 孤立页面（无引用指向）  (0 项)
────────────────────────────────────────────────────────────
  OK  无孤立页面

...

============================================================
  STATUS: 271 ISSUE(S) FOUND
============================================================
```

### 错误标签速查

| 标签 | 含义 | 示例 |
|------|------|------|
| `DEAD` | 死链：指向不存在的页面 | `DEAD  wiki/AI工具谱/...  →  [[页面名]]` |
| `ORPHAN` | 孤立页面：没人引用 | `ORPHAN  wiki/xyz.md` |
| `NOT_INDEXED` | 在磁盘但未在 index.md | `NOT_INDEXED  wiki/新文件.md` |
| `MISSING_FILE` | index.md 引用但磁盘无 | `MISSING_FILE  wiki/删除的文件.md` |
| `MISSING_DIR` | index.md 列出的子目录不存在 | `MISSING_DIR  wiki/不存在的分类/` |
| `BAD_EXT` | wiki/ 中含非 .md 文件 | `BAD_EXT  wiki/图片.png` |
| `STRAY` | raw/ 根目录散落文件 | `STRAY  raw/孤立文件.txt` |
| `BAD_NAME` | raw/ 文件名不符合规范 | `BAD_NAME  raw/分类/没有日期的文件.md` |
| `MISSING_FM` | 缺少 frontmatter 字段 | `MISSING_FM  wiki/...  缺: title, 录入日期` |
| `NO_LINK` | wiki 页面无出站链接 | `NO_LINK  wiki/xyz.md` |
| `NO_WIKI` | raw/ 文件无对应 wiki 萃取页 | `NO_WIKI  raw/分类/文件  (关键词: ...)` |
| `LOG_FMT` | log.md 格式异常 | `LOG_FMT  第15行: 格式错误行` |
| `LEAK` | index/log 混淆 | `LEAK  第8行: [链接](wiki/...)` |
| `UNKNOWN_DIR` | wiki/ 不在白名单的子目录 | `UNKNOWN_DIR  wiki/新分类/` |

---

## 常见场景

### 场景 1：新增 wiki 页面后运行 lint

**症状**：`NOT_INDEXED  wiki/新文件.md`

**原因**：新文件在磁盘上但还未在 index.md 中添加引用

**方案**：
```markdown
# 在 index.md 对应分类中添加
- [新文件名](wiki/分类/新文件)
```

---

### 场景 2：删除 wiki 页面后运行 lint

**症状**：`MISSING_FILE  wiki/删除的文件.md`

**原因**：index.md 中还有指向该文件的链接，但文件已删除

**方案**：
```bash
# 从 index.md 中删除该文件的所有引用
```

---

### 场景 3：README.md 中的双链报死链

**症状**：
```
DEAD  wiki/账号运营/README.md  →  [[20260411_有限理性_适应性工具箱]]
```

**原因**：双链指向的文件在 `raw/个人成长/` 中，不在 `wiki/个人成长/` 中

**方案**：
```markdown
# 方案 A（快速）：改为 Markdown 链接指向 raw/
❌ [[20260411_有限理性]]
✅ [有限理性](raw/个人成长/20260411_有限理性_适应性工具箱)

# 方案 B（推荐）：萃取文件到 wiki/，然后链接到 wiki 页面
✅ [有限理性与决策](wiki/个人成长/有限理性概念页)
```

---

### 场景 4：raw/ 文件有很多没被萃取

**症状**：
```
NO_WIKI  raw/账号运营/20260411_品牌定位.md  (关键词: 品牌定位)
...（100+ 条）
```

**原因**：这是**正常的**。raw/ 是原始资料库，不是所有文件都需要立即萃取

**方案**：
1. **定期审查**：从 NO_WIKI 清单中选择高频参考文件
2. **逐步萃取**：每周挑选 3-5 个高价值文件提炼为 wiki 页面
3. **记录进度**：在 log.md 中记录萃取动作

```markdown
## [2026-04-14] ingest | 萃取3篇账号运营wiki：品牌定位、卡诺模型、复杂系统思维
```

---

### 场景 5：wiki 页面缺少出站链接

**症状**：
```
NO_LINK  wiki/个人成长/新页面.md
```

**原因**：该页面没有指向其他 wiki 页面的链接，形成"孤岛"

**方案**：
```markdown
# 在页面末尾添加关联链接
## 相关阅读
- [[wiki/个人成长/AMCC训练法]]
- [[wiki/知识库架构/知识库运作指南]]
```

---

## 工作流集成

### 日常维护（每周一次）

```bash
# 1. 运行 lint
python "06_Python Scripts/06_工具/wiki_lint.py"

# 2. 查看输出，识别高优先级问题
# 3. 修复 critical 和 high 问题
# 4. 记录到 CLAUDE.md 教训区（如发现新规则）

# 5. 提交更新
git add -A
git commit -m "chore(wiki): lint 检查 + 修复死链/孤立页面"
```

### 新增 wiki 文件的检查清单

```markdown
[ ] 文件名符合 wiki/分类/文件名.md 格式
[ ] 含必填 frontmatter：title, 录入日期
[ ] 至少有一条出站链接（指向其他 wiki 页面）
[ ] 已在 index.md 中添加引用
[ ] 运行 lint 验证：无死链、无孤立
```

---

## 技术细节

### 配置常数

```python
ALLOWED_WIKI_DIRS = {"AI工具谱", "个人成长", "知识库架构", "账号运营", "选题库"}
# wiki/ 下允许的一级子目录白名单

REQUIRED_FRONTMATTER_FIELDS = ["title", "录入日期"]
# wiki 文件的必填 frontmatter 字段

FRONTMATTER_EXEMPT = {"README.md"}
# 豁免 frontmatter 检查的文件名集合

RAW_FILENAME_RE = re.compile(r'^\d{8}_')
# raw/ 文件名应符合的正则表达式（YYYYMMDD_ 前缀）
```

### 链接解析规则

1. **Markdown 链接**：`[文本](path/to/file.md)`
   - 相对于 wiki_root 的路径
   - 可省略 .md 后缀
   
2. **双链**：`[[文件名]]` 或 `[[wiki/分类/文件名]]`
   - 先在 wiki/ 中按 stem（文件名不含扩展名）模糊匹配
   - 如未找到，标记为死链

### 未萃取文件检查算法

```python
# 对于 raw/ 中的每个文件 raw_file
stem = raw_file.stem                    # 文件名（去扩展名）
clean = re.sub(r'^\d{8}_?', '', stem)   # 去掉 YYYYMMDD_ 前缀
if not matched_in_wiki(clean):
    report("NO_WIKI", raw_file)
```

---

## 故障排查

### 问题：脚本无法读取某些 .md 文件

**症状**：输出中出现编码错误

**方案**：脚本已自动处理 Windows 编码问题（UTF-8 + 错误替换）。若仍有问题，检查文件是否真的是 .md 格式。

### 问题：死链数量爆增

**症状**：运行 lint 后发现 100+ 死链

**原因**（按概率）：
1. 新增了指向 raw/ 的双链
2. 误删了 wiki/ 文件
3. 重命名了文件但忘记更新引用

**方案**：
1. 用 `git diff` 对比上次 lint 以来的修改
2. 检查最近编辑的 .md 文件中的链接
3. 恢复误删文件或更新链接

---

## 版本历史

| 版本 | 时间 | 改动 |
|------|------|------|
| v2.1 | 2026-04-13 | 新增[3c]缺失子目录检查、[9]未萃取文件检查；优化报告格式 |
| v2.0 | 2026-04-13 | 首个完整版本，覆盖11个维度 |
| v1.0 | 早期 | 原始版本，仅支持死链和孤立页面检查 |

---

## 联系

遇到脚本问题或有改进建议？

- 在 CLAUDE.md 中记录教训
- 更新 lint_report_*.md 诊断报告
- 在 log.md 中记录改动

脚本维护者：Claude Code
