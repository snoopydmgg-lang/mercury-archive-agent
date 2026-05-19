---
name: habit
description: |
  极简习惯追踪器。记录和查看每日习惯打卡。
  触发方式：「打卡」「记录习惯」「我今天完成了」「查看习惯统计」「我的习惯」
  Habit tracker with natural language interface.
  Triggers: "打卡", "记录习惯", "我今天完成了", "查看习惯统计", "我的习惯"
---

# habit：极简习惯追踪器

## 核心能力

1. **记录打卡** — 一句话触发，自动解析习惯名称
2. **查看统计** — 查看所有习惯或单个习惯的连续打卡天数
3. **查看记录** — 列出最近打卡历史

## 触发模式解析

### 模式 A：记录打卡

用户说：「打卡」「记录习惯」「我今天完成了XXX」

→ 自动提取习惯名称，执行打卡

**支持的表达：**
- 「打卡」→ 询问习惯名
- 「打卡 戒手机」→ 记录「戒手机」
- 「我今天完成了戒手机」→ 记录「戒手机」
- 「今天没刷手机」→ 记录「戒手机」（关键词提取）
- 「记录习惯：戒手机」→ 记录「戒手机」

### 模式 B：查看统计

用户说：「查看习惯统计」「我的习惯」「打卡统计」

→ 执行 `habit_tracker.py stats`，格式化输出

### 模式 C：查看记录

用户说：「查看记录」「最近打卡」「打卡历史」

→ 执行 `habit_tracker.py list`，格式化输出

---

## 执行层

### 依赖脚本

`06_Python Scripts/06_工具/habit_tracker.py`

### Python 路径

`C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe`

### 执行命令模板

```bash
# 记录打卡
"C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe" "E:\1.work\douyin\1.shuixing\06_Python Scripts\06_工具\habit_tracker.py" log <习惯名> --note <备注>

# 查看统计
"C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe" "E:\1.work\douyin\1.shuixing\06_Python Scripts\06_工具\habit_tracker.py" stats

# 查看记录
"C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe" "E:\1.work\douyin\1.shuixing\06_Python Scripts\06_工具\habit_tracker.py" list <习惯名>
```

---

## 自然语言解析规则

当用户说「打卡」相关的话时，按以下顺序尝试解析：

1. **直接提取**：寻找引号或空格后的第一个词组作为习惯名
   - 「打卡 戒手机」→ 习惯 = 「戒手机」
   - 「记录习惯：戒手机」→ 习惯 = 「戒手机」
2. **从完整句中提取**：
   - 「我今天完成了戒手机」→ 习惯 = 「戒手机」
   - 「今天做到戒手机了」→ 习惯 = 「戒手机」
3. **如果无法提取**：询问用户「要记录哪个习惯？」

### 习惯名标准化

- 「戒手机」「不刷手机」「少刷手机」→ 建议统一为「戒手机」
- 「喝水」「多喝水」→ 建议统一为「喝水」
- 「运动」「锻炼」「健身」→ 建议统一为一个名称

---

## 回复模板

### 打卡成功

```
  [打卡成功]
  习惯：{习惯名}
  时间：{HH:MM}
  备注：{备注，如果有}
```

### 统计输出

```
  ## 习惯统计

  习惯              打卡次数
  ─────────────────────────
  戒手机               12次
  喝水                  8次

  ## 连续打卡（近30天）

  戒手机    5天
  喝水      3天
```

### 无数据

```
  暂无打卡记录。
  输入「打卡 习惯名」开始记录你的第一个习惯。
```

---

## 注意事项

- 数据存储在 `06_Python Scripts/06_工具/habit_data/habits.csv`
- 所有数据本地存储，不上传
- 支持备注，用 `--note` 参数传入
