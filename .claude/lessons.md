# 任务教训记录

所有过往任务中发现的问题、解决方案和最佳实践。按日期倒序排列。

---

## 2026-05-21

- **HUD hybrid 架构**：旧 statusline 用 session token delta 算费用，compaction 后失真。新方案：`billing_cache.json`（token_tracker 同步 CSV 写入）= 权威基底，`billing_realtime_state.json`（statusline 写入）= 实时估算基准点。token 增量只做临时估算用 `~` 标记，compaction/session/cache 变化时自动重建基准。自检：`test_statusline.ps1`（8 项测试），恢复：`hud_backup_stable/`
- **PowerShell 5.1 三大限制**：1) 无三元运算符 `?:`，须用 if/else 块 2) 无 `&&`/`||` 管道链，须用 `; if ($?) {}` 3) UTF-8 无 BOM 导致特殊字符解析报错，须 `Set-Content -Encoding UTF8`（带 BOM）或只用 ASCII 安全字符
- **SQLite 表不存在别猜**：billing_daily 表在 DB 中不一定存在，先 `SELECT name FROM sqlite_master WHERE type='table'`，再用 `PRAGMA table_info(name)`
- **git add . 危险**：可能误提交 cookie、billing_cache、realtime_state。须逐个 `git add <文件>`、提交前 `git diff --cached --name-only`、误 stage 用 `git restore --staged <文件>`
- **token_tracker billing_daily 存累计月费**：`billing_daily.official_cost` 是当月累计，非当日增量。sync_billing_daily 改用 `official_info['today_cost']` 写入 daily 字段
- **账单 cache 恢复机制**：CSV 删除后 token_tracker 回退 CALIBRATED_ESTIMATE 模式，Daily 显示 ¥0.00。账单数据在 SQLite 中保留，可手动写 cache JSON 补救

## 2026-05-02

- **Windows `ln -s` 静默降级**：Git Bash 的 `ln -s` 对目录不报错但静默退化为实体文件夹拷贝（exit 0）。正确做法：`cmd //c "mklink /D <link> <target>"`，必须用 `ls -l` 验证首字母为 `l` 且有 `->` 指向
- **Python 被权限系统拦截 (exit 49)**：优先用 Node.js 做 JSON 和文件处理，禁止反复重试 Python。根本解决需在 settings.json 加 allow 规则
- **Skill 更新流程**：通过 `.skill-lock.json` 找到 GitHub 源 repo → clone latest → 对比 `skillFolderHash` → 更新 SKILL.md + lock 文件 → 重建 symlink
- **CLAUDE.md 重构**：306 行/17 章节 → 92 行/6 章节。删 70 行「模块一~四」（与前半部分重复），长报告生成规则缩为踩坑条目，路径速查合并为统一表格
- **.claude/ 子文件维护**：以 Wiki知识库 为信源更新 workflows.md / integrations.md / project-structure.md，wiki 无则从 raw 萃取

---

## 2026-04-30

- **Windows Python PATH 问题**：系统 PATH 可能指向 Windows Store 的 Python stub（返回退出码 49），需临时修改 PATH 指向真实 Python 安装路径：`export PATH="/c/Users/Administrator/AppData/Local/Programs/Python/Python310:$PATH"`
- **Windows 控制台编码**：脚本开头添加 `sys.stdout.reconfigure(encoding='utf-8')` 修复 emoji 和中文显示的 UnicodeEncodeError
- **飞书 API 字段名匹配**：脚本中使用的字段名必须与飞书表格实际字段完全一致，建议先用 API 查询字段列表再编写上传脚本
- **飞书 API 字段查询**：可用 `GET https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields` 获取实际字段列表
- **SSL 连接问题**：lark-oapi SDK 遇到 SSLError 时，可降级到 requests 库直接调用 REST API，开发环境可用 `verify=False` 快速验证（生产环境需解决证书问题）
- **诊断脚本最佳实践**：包含详细日志输出（配置检查、API 响应码、响应消息、异常堆栈），便于快速定位问题
- **Kitta AI TTS API 参数**：必须使用 `reference_id` 而非 `voice_id`，完整参数：`{"text": "...", "reference_id": "...", "version": "s1", "format": "wav"}`

---

## 2026-04-13

- **Wiki Lint 双架构规范**：raw/wiki 分离后，index.md 只列 wiki/ 萃取页（raw/ 不入 index），否则死链。选题背景资料在 raw/选题库/ 中，不创建 wiki/ 副本
- **Wiki Frontmatter 必填**：每个 wiki .md 需含 `title` 和 `录入日期`；README/index 等豁免
- **Wiki 出站链接强制**：每页至少一条链接到其他 wiki 页面（构建知识网络），冷启动期可豁免
- **未萃取文件清单模式**：raw/ 中的原始文件不一定要立即萃取。使用 lint 工具定期扫描，作为**持续改进的工作清单**，优先萃取高频参考文件
- **lint 检查命令行**：`python 06_Python Scripts/06_工具/wiki_lint.py`，覆盖11个维度，包括新增的[9]未萃取文件检查、[3c]缺失子目录检查

---

## 2026-04-11

- **知识库整理**：背景资料、对标博主爆款文案等文案创作素材统一归入 `wiki/选题库/` 和 `wiki/账号运营/`，禁止散落在项目文件夹中
- **memory文件夹维护**：定期清理无关/过时的memory文件，保持精简；合并重复内容（如教训合并）
- **根目录极简原则**：`03_Assets_全局库/` 根目录只保留 index.md、log.md、SCHEMA.md、raw/、wiki/，其他一律移入wiki对应分类

**成品视频归冷备份**：视频成品（.mp4）一律放入 `02_Archive_冷备份/`，不留在 `01_Projects_制作中/`

**全局库只进.md**：进入 `03_Assets_全局库/wiki/` 的文件必须是 .md 格式，非 md 文件（如图片）放入冷备份

**两个知识库**（与飞书无关）：
- **Get笔记知识库** — Get笔记 App 订阅的博主文案，skill: `extract-getnote-articles` 爬取
- **全局库**（`03_Assets_全局库/`）— 本地资产库：raw/（只读）+ wiki/（萃取）+ index.md（空间拓扑）+ log.md（时间日志）

**全局库架构规范**（2026-04-12 新增）：
- `index.md` — 空间拓扑（目录索引），严格与日志分离
- `log.md` — 时间序列（Append-only 操作日志）
- `wiki/` — 萃取文档，强制交叉引用（实体页/概念页/对比页）
- `raw/` — 原始资料，只读不修改

**Query Write-back 机制**：复杂查询/高价值推演必须沉淀为独立 Wiki 页面，并在 log.md 追加记录。

**数据分析工作流**：下载数据 → 放入 `04_数据分析结果/` → 分析提炼 → 有价值内容写入 `wiki/账号运营/` → 原始数据删除（不留恋文件本身）

**知识库健康检查**：`python 06_Python Scripts/06_工具/wiki_lint.py`

---

## 2026-04-01

- **winget --all-versions危险**：会删除该ID下所有版本，先查版本再精确卸载
- **Windows Store Stub**：需在设置→应用→应用执行别名中关闭
- **豆包字幕背景**：加`--no-cover-rules`，16:9用2560x1440

---

## 2026-03-30

- **豆包图生图中文问题**：`--no-cover-rules`禁用封面规则，脚本默认规则不应影响所有场景

---

## 2026-03-27

- **Windows Python路径**：必须用完整路径执行脚本
- **Todoist执行**：同样需要完整Python路径
- **多版本文案镜头**：先汇总共性镜头形成"一次性拍摄清单"

---

## 2026-03-26

- **tar路径格式**：Windows Git Bash用`/e/`格式不用`E:/`
- **大型npm打包**：用Python tarfile需耐心等待2-3分钟
- **离线部署**：优先本地收件箱找安装包

---

## 2026-03-25

- **Python字符串中文引号**：用`\u201c`/`\u201d`转义或单引号包裹
- **Gradio兼容性**：服务端用4.44.0，gradio_client自动降级到1.3.0
- **NLTK报错**：需`nltk.download('averaged_perceptron_tagger_eng', quiet=True)`
- **专用脚本策略**：有大量背景数据的产品建专用脚本效果更好
- **收件箱清理**：用户说"全部删掉"就直接执行

---

## 2026-03-17

- **Playwright MCP**：无法继承浏览器登录信息
- **浏览器扩展**：需用户手动安装到已登录浏览器
- **根目录极简化**：定期清理临时文件
