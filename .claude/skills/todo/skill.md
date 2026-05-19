# Todoist 待办管理

## 功能

1. **查看待办** - 读取所有待办事项，按日期分组展示
2. **添加待办** - 创建新待办，支持设置日期、优先级
3. **完成待办** - 将待办标记为已完成
4. **删除待办** - 删除指定的待办
5. **查看今天/明天** - 按日期筛选待办

## API 配置

- **API Token**: `888ac3d6924775c0deb56efab3086e1553ef9cf9`
- **API Base**: `https://api.todoist.com/api/v1`

## 脚本位置

`06_Python Scripts/07_Todoist/`

- `todoist_api.py` - Todoist API 封装

## 使用示例

```bash
# 查看所有待办
cd "06_Python Scripts/07_Todoist" && python todoist_api.py list

# 查看今天的待办
cd "06_Python Scripts/07_Todoist" && python todoist_api.py today

# 添加待办
cd "06_Python Scripts/07_Todoist" && python todoist_api.py add "任务内容" --date "2026-03-28"

# 添加带优先级的待办 (p1=p4, p2=p3, p3=p2, p4=p1)
cd "06_Python Scripts/07_Todoist" && python todoist_api.py add "任务内容" --priority p1

# 完成待办
cd "06_Python Scripts/07_Todoist" && python todoist_api.py close <task_id>

# 删除待办
cd "06_Python Scripts/07_Todoist" && python todoist_api.py delete <task_id>
```

## 绝对规则

**禁止**生成任何与外包(outsourcing/外包)相关的任务。

## 触发词

- "查看待办"、"我的待办"、"todo list"
- "今天干什么"、"明天干什么"
- "添加待办"、"新建任务"
- "完成任务"、"删除待办"
