#!/usr/bin/env python3
"""
Todoist API 封装脚本
支持：查看、添加、完成、删除待办
"""

import requests
import sys
import json
import io
from datetime import datetime, timedelta

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# API 配置
API_TOKEN = "888ac3d6924775c0deb56efab3086e1553ef9cf9"
API_BASE = "https://api.todoist.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def get_tasks():
    """获取所有待办"""
    resp = requests.get(f"{API_BASE}/tasks", headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("results", [])

def add_task(content, date=None, priority=None, parent_id=None):
    """添加待办"""
    data = {"content": content}
    if date:
        data["due_date"] = date
    if priority:
        # Todoist priority: 1 (urgent) to 4 (normal)
        priority_map = {"p1": 1, "p2": 2, "p3": 3, "p4": 4}
        data["priority"] = priority_map.get(priority, 4)
    if parent_id:
        data["parent_id"] = parent_id

    resp = requests.post(f"{API_BASE}/tasks", headers=HEADERS, json=data)
    resp.raise_for_status()
    return resp.json()

def close_task(task_id):
    """完成任务"""
    resp = requests.post(f"{API_BASE}/tasks/{task_id}/close", headers=HEADERS)
    resp.raise_for_status()
    return True

def delete_task(task_id):
    """删除待办"""
    resp = requests.delete(f"{API_BASE}/tasks/{task_id}", headers=HEADERS)
    resp.raise_for_status()
    return True

def format_tasks(tasks, filter_date=None):
    """格式化输出待办"""
    priority_map = {1: "P1(紧急)", 2: "P2", 3: "P3", 4: "P4"}

    # 按日期分组
    groups = {}
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    for task in tasks:
        if task.get("is_deleted") or task.get("checked"):
            continue

        due = task.get("due", {})
        due_date = due.get("date", "无日期") if due else "无日期"

        if filter_date == "today":
            if due_date != today:
                continue
        elif filter_date == "tomorrow":
            target = tomorrow
            if due_date != target:
                continue
        elif filter_date == "week":
            # 本周
            try:
                task_date = datetime.strptime(due_date, "%Y-%m-%d")
                today_dt = datetime.strptime(today, "%Y-%m-%d")
                week_end = today_dt + timedelta(days=7)
                if task_date < today_dt or task_date > week_end:
                    continue
            except:
                if due_date == "无日期":
                    pass
                else:
                    continue

        # 显示名称
        date_display = due_date
        if due_date == today:
            date_display = "今天"
        elif due_date == tomorrow:
            date_display = "明天"

        priority = task.get("priority", 4)
        content = task.get("content", "")
        task_id = task.get("id", "")

        group_key = date_display
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append((priority_map.get(priority, "P4"), content, task_id))

    # 输出
    if not groups:
        print("没有待办事项")
        return

    for date_group in sorted(groups.keys()):
        print(f"\n### {date_group}（{len(groups[date_group])}条）")
        print("| 优先级 | 内容 | ID |")
        print("|-------|------|----|")
        for p, content, task_id in sorted(groups[date_group]):
            print(f"| {p} | {content} | `{task_id}` |")

def cmd_list():
    """列出所有待办"""
    tasks = get_tasks()
    format_tasks(tasks)

def cmd_today():
    """列出今天的待办"""
    tasks = get_tasks()
    format_tasks(tasks, filter_date="today")

def cmd_tomorrow():
    """列出明天的待办"""
    tasks = get_tasks()
    format_tasks(tasks, filter_date="tomorrow")

def cmd_week():
    """列出本周的待办"""
    tasks = get_tasks()
    format_tasks(tasks, filter_date="week")

def cmd_add(content, date=None, priority=None, parent_id=None):
    """添加待办"""
    task = add_task(content, date, priority, parent_id)
    print(f"已添加: {task.get('content')} (ID: {task.get('id')})")

def cmd_close(task_id):
    """完成任务"""
    close_task(task_id)
    print(f"已完成任务: {task_id}")

def cmd_delete(task_id):
    """删除待办"""
    delete_task(task_id)
    print(f"已删除任务: {task_id}")

def cmd_search_delete(keyword):
    """搜索并删除包含关键词的任务"""
    tasks = get_tasks()
    deleted = []
    for task in tasks:
        if task.get("is_deleted") or task.get("checked"):
            continue
        if keyword.lower() in task.get("content", "").lower():
            delete_task(task["id"])
            deleted.append(task["content"])
            print(f"已删除: {task['content']}")
    if not deleted:
        print(f"未找到包含 '{keyword}' 的任务")
    else:
        print(f"\n共删除 {len(deleted)} 个任务")

def usage():
    print("""Todoist API 用法:
  python todoist_api.py list              # 列出所有待办
  python todoist_api.py today            # 列出今天的待办
  python todoist_api.py tomorrow          # 列出明天的待办
  python todoist_api.py week              # 列出本周的待办
  python todoist_api.py add "内容"        # 添加待办
  python todoist_api.py add "内容" --date "2026-03-28"  # 添加带日期的待办
  python todoist_api.py add "内容" --priority p1         # 添加紧急待办
  python todoist_api.py close <task_id>  # 完成任务
  python todoist_api.py delete <task_id> # 删除待办
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list()
    elif cmd == "today":
        cmd_today()
    elif cmd == "tomorrow":
        cmd_tomorrow()
    elif cmd == "week":
        cmd_week()
    elif cmd == "add":
        content = sys.argv[2] if len(sys.argv) > 2 else ""
        if not content:
            print("请提供待办内容")
            sys.exit(1)

        date = None
        priority = None
        parent_id = None

        # 解析可选参数
        args = sys.argv[3:]
        i = 0
        while i < len(args):
            if args[i] == "--date" and i + 1 < len(args):
                date = args[i + 1]
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                priority = args[i + 1]
                i += 2
            elif args[i] == "--parent" and i + 1 < len(args):
                parent_id = args[i + 1]
                i += 2
            else:
                i += 1

        cmd_add(content, date, priority, parent_id)
    elif cmd == "close":
        if len(sys.argv) < 3:
            print("请提供 task_id")
            sys.exit(1)
        cmd_close(sys.argv[2])
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("请提供 task_id")
            sys.exit(1)
        cmd_delete(sys.argv[2])
    elif cmd == "search-delete":
        if len(sys.argv) < 3:
            print("请提供关键词")
            sys.exit(1)
        cmd_search_delete(sys.argv[2])
    else:
        usage()
