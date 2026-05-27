#!/usr/bin/env python3
"""添加足部/甲癣康复计划到Todoist"""
import requests, time
from datetime import datetime, timedelta

API_TOKEN = '888ac3d6924775c0deb56efab3086e1553ef9cf9'
API_BASE = 'https://api.todoist.com/api/v1'
HEADERS = {'Authorization': f'Bearer {API_TOKEN}', 'Content-Type': 'application/json'}

def add_task(content, date=None, priority=None, parent_id=None, retries=3):
    data = {'content': content}
    if date: data['due_date'] = date
    if priority: data['priority'] = priority
    if parent_id: data['parent_id'] = parent_id
    for attempt in range(retries):
        try:
            resp = requests.post(f'{API_BASE}/tasks', headers=HEADERS, json=data, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f'  重试 {attempt+1}: {e}')
            time.sleep(2)
    return None

def get_tasks():
    try:
        resp = requests.get(f'{API_BASE}/tasks', headers=HEADERS, timeout=15)
        return resp.json().get('results', [])
    except:
        return []

start = datetime(2026, 5, 27)

# ===== 1. 足癣每日任务：挂在已有周任务下 =====
print('=== 足癣每日任务 ===')
existing = get_tasks()
week_ids = {}
for t in existing:
    content = t.get('content', '')
    for i in range(1, 5):
        if content.startswith(f'第{i}周'):
            week_ids[i] = t['id']

# 更新已有的每日任务（之前标了特比萘芬5/28到货）
# 新增：独立的足癣护理任务
for week_idx in range(1, 5):
    week_start = start + timedelta(days=(week_idx - 1) * 7)
    date_str = week_start.strftime('%Y-%m-%d')
    parent = week_ids.get(week_idx)
    if parent:
        add_task(
            '[每天足癣] 洗脚擦干 → 特比萘芬涂全脚底+趾缝（症状消失后继续4周）',
            date=date_str, parent_id=parent, priority=2
        )
        print(f'  第{week_idx}周 足癣每日项')
        time.sleep(0.5)

# ===== 2. 灰指甲周计划（周日封包 + 周一清创上漆）=====
print('\n=== 灰指甲周计划 ===')
nail_parent = add_task('灰指甲康复计划（尿素霜+阿莫罗芬，持续至新甲长出）', date='2026-05-27', priority=2)
nail_parent_id = nail_parent['id'] if nail_parent else None
print(f'  父任务: {nail_parent_id}')

# 生成12周的周日+周一任务（覆盖前3个月密集治疗期）
for week in range(12):
    sunday = start + timedelta(days=(6 - start.weekday()) % 7 + 7 * (week - 1))
    if week == 0:
        # 第一个周日：5/31
        sunday = datetime(2026, 5, 31)
    monday = sunday + timedelta(days=1)

    sun_str = sunday.strftime('%Y-%m-%d')
    mon_str = monday.strftime('%Y-%m-%d')

    # 周日：封包
    add_task(
        f'灰指甲第{week+1}次：磨薄病甲 → 尿素霜厚涂 → 保鲜膜封包过夜',
        date=sun_str, parent_id=nail_parent_id, priority=1
    )
    print(f'  {sun_str} 周日 封包')
    time.sleep(0.3)

    # 周一：清创+上漆
    add_task(
        f'灰指甲第{week+1}次：剔除软化角质 → 阿莫罗芬搽剂涂病甲',
        date=mon_str, parent_id=nail_parent_id, priority=1
    )
    print(f'  {mon_str} 周一 清创上漆')
    time.sleep(0.3)

# 3个月评估节点
eval_date = (start + timedelta(days=90)).strftime('%Y-%m-%d')
add_task(
    '灰指甲3个月评估：新甲是否从根部长出？未改善 → 皮肤科复诊',
    date=eval_date, parent_id=nail_parent_id, priority=1
)
print(f'\n  评估节点: {eval_date}')

print('\n=== 完成 ===')
