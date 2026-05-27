#!/usr/bin/env python3
"""清理重复任务 + 更新今天的任务"""
import requests, time
from collections import defaultdict

API_TOKEN = '888ac3d6924775c0deb56efab3086e1553ef9cf9'
API_BASE = 'https://api.todoist.com/api/v1'
HEADERS = {'Authorization': f'Bearer {API_TOKEN}', 'Content-Type': 'application/json'}

resp = requests.get(f'{API_BASE}/tasks', headers=HEADERS, timeout=15)
tasks = resp.json().get('results', [])

# 按内容分组
groups = defaultdict(list)
for t in tasks:
    if not t.get('is_deleted') and not t.get('checked'):
        groups[t['content']].append(t)

# 删除重复（每个内容只保留第一个）
deleted = 0
for content, task_list in groups.items():
    if len(task_list) > 1:
        for t in task_list[1:]:
            tid = t['id']
            requests.delete(f'{API_BASE}/tasks/{tid}', headers=HEADERS, timeout=10)
            deleted += 1
            time.sleep(0.3)

print(f'已删除 {deleted} 个重复任务')

# 再次获取
time.sleep(1)
resp = requests.get(f'{API_BASE}/tasks', headers=HEADERS, timeout=15)
tasks = resp.json().get('results', [])

# 更新今天 5/27 的洗发任务
for t in tasks:
    content = t.get('content', '')
    due_date = t.get('due', {}).get('date', '')
    tid = t['id']
    if '酮康唑洗剂' in content and '夫西地酸' in content and due_date == '2026-05-27':
        new_content = '洗发：水杨酸软膏(15min) → 酮康唑洗剂(5min) | 夫西地酸明天到货再涂'
        requests.post(f'{API_BASE}/tasks/{tid}', headers=HEADERS, json={'content': new_content}, timeout=10)
        print(f'已更新今天洗发任务')
        time.sleep(0.3)
        break

# 更新每日任务
for t in tasks:
    content = t.get('content', '')
    tid = t['id']
    if '特比萘芬涂脚底' in content and '到货' not in content:
        new_content = '[每天] 早：鱼油+锌 | 晚：鱼油+锌 | 洗脚后：特比萘芬涂脚底(5/28到货后开始)'
        requests.post(f'{API_BASE}/tasks/{tid}', headers=HEADERS, json={'content': new_content}, timeout=10)
        print(f'已更新每日任务: 标注特比萘芬5/28到货')
        time.sleep(0.3)

print('完成')
