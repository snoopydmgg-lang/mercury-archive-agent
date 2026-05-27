#!/usr/bin/env python3
"""创建4周治疗计划 - 带重试机制"""

import requests
import sys
import io
import time
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_TOKEN = "888ac3d6924775c0deb56efab3086e1553ef9cf9"
API_BASE = "https://api.todoist.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def add_task(content, date=None, priority=None, parent_id=None, retries=3):
    data = {"content": content}
    if date:
        data["due_date"] = date
    if priority:
        data["priority"] = priority
    if parent_id:
        data["parent_id"] = parent_id
    for attempt in range(retries):
        try:
            resp = requests.post(f"{API_BASE}/tasks", headers=HEADERS, json=data, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"  [重试 {attempt+1}/{retries}] {content[:30]}... 错误: {e}")
            time.sleep(2)
    print(f"  [失败] 跳过: {content[:40]}")
    return None

def get_existing_tasks():
    try:
        resp = requests.get(f"{API_BASE}/tasks", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except:
        return []

# 检查已有任务
print("=== 检查已有任务 ===")
existing = get_existing_tasks()
existing_contents = set()
for t in existing:
    if not t.get("is_deleted") and not t.get("checked"):
        existing_contents.add(t.get("content", ""))
print(f"已有 {len(existing_contents)} 个活跃任务\n")

start = datetime(2026, 5, 27)
wash_days = [start + timedelta(days=i) for i in range(0, 28, 2)]
shampoos = ["酮康唑洗剂", "二硫化硒洗剂"]

nail_sundays = []
d = start
while d < start + timedelta(days=28):
    if d.weekday() == 6:
        nail_sundays.append(d)
    d += timedelta(days=1)

week_ranges = [
    (0, "第1周 (5/27-6/2)", "2026-05-27"),
    (1, "第2周 (6/3-6/9)", "2026-06-03"),
    (2, "第3周 (6/10-6/16)", "2026-06-10"),
    (3, "第4周 (6/17-6/23)", "2026-06-17"),
]

# 查找或创建父任务
week_ids = {}
for idx, name, date in week_ranges:
    # 检查是否已存在
    found = None
    for t in existing:
        if t.get("content", "").startswith(f"第{idx+1}周"):
            found = t["id"]
            break
    if found:
        week_ids[idx] = found
        print(f"[已存在] {name} → {found}")
    else:
        task = add_task(name, date=date, priority=2)
        if task:
            week_ids[idx] = task["id"]
            print(f"[新建] {name} → {task['id']}")
        time.sleep(0.5)

def get_week_idx(d):
    return min((d - start).days // 7, 3)

# 创建洗发日任务（跳过已存在的）
print("\n--- 洗发日 ---")
for i, wash_date in enumerate(wash_days):
    shampoo = shampoos[i % 2]
    date_str = wash_date.strftime("%Y-%m-%d")
    content = f"洗发：水杨酸软膏(15min) → {shampoo}(5min) → 夫西地酸点涂"
    if content in existing_contents:
        print(f"  {date_str} [已存在] 跳过")
        continue
    week_idx = get_week_idx(wash_date)
    result = add_task(content, date=date_str, parent_id=week_ids.get(week_idx), priority=1)
    if result:
        print(f"  {date_str} → {shampoo}")
    time.sleep(0.5)

# 创建灰指甲任务
print("\n--- 灰指甲日 ---")
for nail_date in nail_sundays:
    date_str = nail_date.strftime("%Y-%m-%d")
    content = "灰指甲：尿素霜封包过夜 → 次日晨清创 → 阿莫罗芬搽剂"
    if content in existing_contents:
        print(f"  {date_str} [已存在] 跳过")
        continue
    week_idx = get_week_idx(nail_date)
    result = add_task(content, date=date_str, parent_id=week_ids.get(week_idx), priority=1)
    if result:
        print(f"  {date_str} (周日)")
    time.sleep(0.5)

# 每日固定项
print("\n--- 每日固定项 ---")
daily_content = "[每天] 早：鱼油+锌 | 晚：鱼油+锌 | 洗脚后：特比萘芬涂脚底"
for idx, name, date in week_ranges:
    if daily_content in existing_contents:
        print(f"  {name} [已存在] 跳过")
        continue
    result = add_task(daily_content, date=date, parent_id=week_ids.get(idx), priority=2)
    if result:
        print(f"  {name}")
    time.sleep(0.5)

# 第4周末评估
eval_content = "第4周末评估：头皮瘙痒是否下降70%？未达标 → 挂号皮肤科+风湿免疫科"
if eval_content not in existing_contents:
    add_task(eval_content, date="2026-06-23", parent_id=week_ids.get(3), priority=1)
    print("\n[评估节点] 6/23")

print("\n=== 完成 ===")
