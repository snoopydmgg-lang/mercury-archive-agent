---
name: tomato-todo
description: "番茄ToDo 管理工具。用于管理待办事项、记录番茄时间、自动计算番茄数。示例：\"查看待办\", \"添加任务\", \"导入任务\", \"查看统计\", \"查看记录\""
---

# 番茄ToDo CLI 工具

通过命令行管理番茄ToDo的待办事项和番茄记录，支持批量导入和自动计算番茄数。

## 数据位置

- **数据库**: `C:\Users\Administrator\AppData\Roaming\番茄ToDo\tomatodo_db.json`
- **程序**: `D:\TODOlist\TomaToDo.exe`

## 核心功能

| 功能 | 说明 |
|------|------|
| 列出待办 | 显示所有待办事项 |
| 添加待办 | 添加新的待办任务 |
| 导入任务 | 批量导入任务，自动计算所需番茄数 |
| 完成任务 | 增加完成计数 |
| 删除待办 | 删除待办事项 |
| 重置待办 | 将待办重置为未完成 |
| 统计信息 | 显示番茄时间统计 |
| 番茄记录 | 显示已完成的历史记录 |

## 代码位置

`E:\1.work\douyin\1.shuixing\06_Python Scripts\09_番茄Todo工具\tomato_cli.py`

## 使用方法

### 基本流程

1. **理解用户需求** - 用户需要管理番茄ToDo时使用
2. **执行对应命令**
3. **返回执行结果**

### 命令语法

```bash
# Python 路径
PYTHON="C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe"

# 列出待办
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" list

# 列出待办（包含已完成的）
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" list --all

# 添加待办（名称 时间(分钟) 分类）
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" add "写代码" 30
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" add "读书" 25 工作

# 批量导入任务（自动计算番茄数）
# 格式: "任务名,预计分钟数"
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" import "写代码,60" "读书,30" "开会,45"

# 完成任务（增加番茄计数）
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" done <ID>

# 删除待办
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" delete <ID>

# 重置待办为未完成
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" reset <ID>

# 显示统计
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" stats

# 显示番茄记录
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" records
"$PYTHON" "E:/1.work/douyin/1.shuixing/06_Python Scripts/09_番茄Todo工具/tomato_cli.py" records 20  # 显示20条

# 打开番茄ToDo应用
cmd /c "D:\TODOlist\TomaToDo.exe"
```

## 番茄数计算规则

每个番茄 = 25分钟工作 + 5分钟休息 = 30分钟周期

向上取整：`番茄数 = ceil(总分钟数 / 30)`

| 总时间 | 番茄数 | 工作时间 | 休息时间 |
|--------|--------|----------|----------|
| 60分钟 | 2个 | 50分钟 | 10分钟 |
| 90分钟 | 3个 | 75分钟 | 15分钟 |
| 120分钟 | 4个 | 100分钟 | 20分钟 |
| 150分钟 | 5个 | 125分钟 | 25分钟 |

## 触发关键词

当用户说以下话时使用此 skill：
- "查看待办"
- "我的待办"
- "还有什么任务"
- "添加任务"
- "新任务"
- "导入任务"
- "今日任务"
- "完成任务"
- "做完了"
- "删除任务"
- "番茄统计"
- "我完成了多少"
- "番茄记录"
- "查看记录"
- "打开番茄"
- "启动番茄ToDo"
- 其他番茄相关操作

## 注意事项

1. **数据库**: 数据存储在 JSON 文件中，修改后需重启番茄ToDo应用才能同步
2. **ID 查找**: 使用 `list` 命令查看待办的 ID
3. **完成机制**: `done` 命令是增加完成计数，不是删除待办
4. **导入确认**: 批量导入会显示预览并要求确认
5. **数据同步**: 如果使用手机端同步，需要在应用中操作
6. **【重要】批量导入后自动重启**: 每次批量导入任务后，必须自动执行 `cmd /c "D:\TODOlist\TomaToDo.exe"` 重启应用，否则新任务不会显示

## 数据结构

```json
{
  "PCToDo": [...],       // 待办事项列表
  "PCRecord": [...],       // 完成记录
  "PCDeletedTodo": [],     // 已删除的待办
  "todoIdCounter": 246,    // ID计数器
  "recordIdCounter": 69    // 记录计数器
}
```

## 待办事项字段说明

| 字段 | 说明 |
|------|------|
| ID | 唯一标识符 |
| name | 任务名称 |
| time | 单个番茄时长（默认25分钟） |
| isComplied | 已完成次数（0=未完成） |
| i5 | 计划番茄数（批量导入时自动计算） |
| s1 | 分类标签 |
| s2 | 创建时间戳 |
```

<System_Constraints>
# 待办系统核心物理法则 (绝对不可违反)
1. 产能模型：每周硬上限 66 个番茄钟（每天 11 个）。排期算法必须基于此计算。
2. 零外包原则：绝对禁止生成、恢复或保留任何与"外包"、"outsourcing"相关的任务。所有任务默认单人执行。
3. 结构化降维：所有写入 Todoist 的任务必须通过 parent_id 建立严格的父子层级嵌套，禁止使用扁平的字符串拼接（如"父任务-子任务"）。
4. 状态机防重：调用 GetNote 提取笔记后，必须与 06_Python Scripts/07_Todoist/sync_state.json 进行比对，仅处理未记录的 ID，处理后必须更新该 JSON。
5. 双轨调度引擎：排期必须先读取 weekly_baseline.json 铺排固定的 7 个视频生产流水线，剩余番茄钟空槽才允许填充从笔记提取的动态任务。
6. 康复期禁令：排期时绝对避开任何上肢训练任务。
</System_Constraints>

<Troubleshooting_Protocols>
# 系统修改与排障 SOP (当用户提出不满或修改需求时严格执行)
1. 拦截与诊断：当用户提出修改需求时，首先核对 <System_Constraints>，确认修改是否会破坏产能平衡或防重机制。
2. 根因分析 (RCA)：遇到 Bug（如任务重复、排期溢出），禁止提供表面补救。必须先读取 sync_state.json 或 weekly_baseline.json 的当前状态，定位是"状态机失效"还是"基线产能计算错误"。
3. 最小权限修改：修改 Python 脚本时，优先修改 weekly_planner.py 中的调度逻辑或 todoist_api.py 中的参数传递，不要重构整个文件。
4. 终端优先：在提供解决方案时，直接输出可执行的 bash/python 代码块或 Claude CLI 指令，拒绝解释性废话。
</Troubleshooting_Protocols>
