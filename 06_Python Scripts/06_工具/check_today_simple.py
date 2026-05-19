#!/usr/bin/env python3
import requests
from datetime import datetime

API_TOKEN = "888ac3d6924775c0deb56efab3086e1553ef9cf9"
API_BASE = "https://api.todoist.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# 获取所有任务
resp = requests.get(f"{API_BASE}/tasks", headers=HEADERS)
resp.raise_for_status()
tasks = resp.json().get("results", [])

# 筛选今天的任务
today = datetime.now().strftime("%Y-%m-%d")
today_tasks = []

for task in tasks:
    if task.get("is_deleted") or task.get("checked"):
        continue
    due = task.get("due", {})
    due_date = due.get("date", "") if due else ""
    if due_date == today:
        today_tasks.append(task)

# 输出
if today_tasks:
    print(f"\n### 今天（{len(today_tasks)}条）")
    print("| 优先级 | 内容 | ID |")
    print("|-------|------|----|")

    priority_map = {1: "P1(紧急)", 2: "P2", 3: "P3", 4: "P4"}
    for task in today_tasks:
        priority = task.get("priority", 4)
        content = task.get("content", "")
        task_id = task.get("id", "")
        print(f"| {priority_map.get(priority, 'P4')} | {content} | `{task_id}` |")
else:
    print("没有待办事项")
