#!/usr/bin/env python3
"""
周计划自动化脚本 - 双轨调度逻辑
从 GetNote 日记提取 [PAIN]/[GOAL] 标签内容，转化为 Todoist 父子任务

双轨调度:
1. 基线铺排: 读取 weekly_baseline.json，将固定任务写入 Todoist
2. 动态填充: 调用 GetNote 提取新笔记，分配到剩余番茄空槽

产能模型:
- 每小时2番茄，连续3轮后休息15分钟
- 默认每天6小时工作 = 11有效番茄
- 每周(6天) = 66番茄

约束:
- 禁止生成外包任务
- 禁止上肢训练任务（腱鞘炎康复期）
- 每天总番茄数不超过11个
"""

import requests
import json
import sys
import io
import re
import os
from datetime import datetime, timedelta
from pathlib import Path

# 代理设置
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# GetNote API 配置
GETNOTE_BASE_URL = "https://openapi.biji.com/open/api/v1"
GETNOTE_API_KEY = "gk_live_87da6636661e7a8f.2a2462e2bb6c3f98e976a4404f96d27254e0f3f7ea634aab"
GETNOTE_CLIENT_ID = "cli_62e1e5fb96c7211b1b02c62e"

GETNOTE_HEADERS = {
    "X-Client-ID": GETNOTE_CLIENT_ID,
    "Authorization": GETNOTE_API_KEY,
    "Content-Type": "application/json"
}

# Todoist API 配置
TODOIST_API_TOKEN = "888ac3d6924775c0deb56efab3086e1553ef9cf9"
TODOIST_API_BASE = "https://api.todoist.com/api/v1"
TODOIST_HEADERS = {
    "Authorization": f"Bearer {TODOIST_API_TOKEN}",
    "Content-Type": "application/json"
}

# ============ GetNote 函数 ============

def get_note_list(since_id: int = 0, limit: int = 50):
    """获取笔记列表"""
    resp = requests.get(
        f"{GETNOTE_BASE_URL}/resource/note/list",
        headers=GETNOTE_HEADERS,
        params={"since_id": since_id, "limit": limit}
    )
    return resp.json()

def semantic_recall(query: str, limit: int = 10):
    """语义召回笔记"""
    data = {"query": query, "limit": limit}
    resp = requests.post(
        f"{GETNOTE_BASE_URL}/resource/recall",
        headers=GETNOTE_HEADERS,
        json=data
    )
    return resp.json()

def get_knowledge_list():
    """获取知识库列表"""
    resp = requests.get(f"{GETNOTE_BASE_URL}/resource/knowledge/list", headers=GETNOTE_HEADERS)
    return resp.json()

# ============ Todoist 函数 ============

def get_tasks():
    """获取所有待办"""
    resp = requests.get(f"{TODOIST_API_BASE}/tasks", headers=TODOIST_HEADERS)
    resp.raise_for_status()
    return resp.json().get("results", [])

def add_task(content, date=None, priority=None, parent_id=None):
    """添加待办"""
    data = {"content": content}
    if date:
        data["due_date"] = date
    if priority:
        priority_map = {"p1": 1, "p2": 2, "p3": 3, "p4": 4}
        data["priority"] = priority_map.get(priority, 4)
    if parent_id:
        data["parent_id"] = parent_id

    resp = requests.post(f"{TODOIST_API_BASE}/tasks", headers=TODOIST_HEADERS, json=data)
    resp.raise_for_status()
    return resp.json()

# ============ 同步状态管理 ============

SYNC_STATE_FILE = Path(__file__).parent / "sync_state.json"

def load_sync_state():
    """读取 sync_state.json"""
    if SYNC_STATE_FILE.exists():
        with open(SYNC_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed_note_ids": [], "last_sync_at": None, "version": 1}

def save_sync_state(state):
    """保存 sync_state.json"""
    with open(SYNC_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def filter_unprocessed_notes(notes, sync_state):
    """过滤掉已处理的笔记ID"""
    processed_ids = set(sync_state.get("processed_note_ids", []))
    return [n for n in notes if str(n.get("note_id")) not in processed_ids]

def mark_notes_processed(note_ids, sync_state):
    """标记笔记为已处理"""
    sync_state["processed_note_ids"].extend([str(nid) for nid in note_ids])
    sync_state["processed_note_ids"] = list(set(sync_state["processed_note_ids"]))
    sync_state["last_sync_at"] = datetime.now().isoformat()
    save_sync_state(sync_state)

# ============ 基线任务管理 ============

BASELINE_FILE = Path(__file__).parent / "weekly_baseline.json"
MAX_DAILY_POMODOROS = 11

def load_baseline():
    """读取 weekly_baseline.json"""
    if BASELINE_FILE.exists():
        with open(BASELINE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def get_weekday_date(weekday_name, offset_weeks=0):
    """获取下一个指定星期X的日期"""
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    target_day = weekdays.index(weekday_name)

    today = datetime.now()
    days_ahead = target_day - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    days_ahead += offset_weeks * 7

    next_date = today + timedelta(days=days_ahead)
    return next_date.strftime("%Y-%m-%d")

def schedule_baseline_tasks():
    """
    【步骤1：基线锁仓】
    读取 weekly_baseline.json，按星期几将任务写入 Todoist
    计算每天已消耗的番茄钟（包括每日Routine + 每周任务）
    """
    baseline = load_baseline()
    if not baseline:
        print("⚠️ 未找到 weekly_baseline.json，跳过基线任务")
        return [], {}

    print("=" * 50)
    print("📌 步骤1：基线锁仓")
    print("=" * 50)

    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # 初始化每日番茄槽
    daily_consumed = {day: 0 for day in WEEKDAYS}
    scheduled_tasks = []
    total_baseline_pomos = 0

    # 处理每日例行任务 (daily_routines) - 每个工作日都要执行
    daily_routines = baseline.get("daily_routines", [])
    for routine in daily_routines:
        task_name = routine.get("task_name", "")
        label = routine.get("label", "[ROUTINE]")
        pomodoros = routine.get("pomodoros", 0.5)

        for day in WEEKDAYS:
            task_date = get_weekday_date(day)
            parent = {
                "content": f"{label} {task_name}",
                "date": task_date,
                "priority": "p3",
                "children": [],
                "source": "baseline",
                "pomodoros": pomodoros
            }
            scheduled_tasks.append(parent)
            daily_consumed[day] += pomodoros
            total_baseline_pomos += pomodoros
            print(f"  {label} {task_name} → {day}({pomodoros}番茄)")

    # 处理每周任务 (weekly_tasks，按星期组织)
    weekly_tasks = baseline.get("weekly_tasks", {})
    for weekday, tasks in weekly_tasks.items():
        if weekday not in WEEKDAYS:
            continue
        for task in tasks:
            task_name = task.get("task_name", "")
            label = task.get("label", "[KERNEL]")
            pomodoros = task.get("pomodoros", 1)

            task_date = get_weekday_date(weekday)
            parent = {
                "content": f"{label} {task_name}",
                "date": task_date,
                "priority": "p2",
                "children": [],
                "source": "baseline",
                "pomodoros": pomodoros
            }
            scheduled_tasks.append(parent)
            daily_consumed[weekday] += pomodoros
            total_baseline_pomos += pomodoros
            print(f"  {label} {task_name} → {weekday}({pomodoros}番茄)")

    print(f"\n📊 基线任务: {len(scheduled_tasks)}个, 总计{total_baseline_pomos}番茄")
    print(f"📊 每日基线消耗:")
    for day in WEEKDAYS:
        print(f"   {day}: {daily_consumed[day]}番茄")

    return scheduled_tasks, daily_consumed, total_baseline_pomos


def schedule_dynamic_tasks(pain_points, daily_consumed):
    """
    【步骤2：产能计算】+【步骤3：动态填充】+【步骤4：熔断机制】
    计算每天剩余空槽，将动态任务填入，超出部分标记为 Backlog
    """
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    print("\n" + "=" * 50)
    print("📌 步骤2+3+4：动态填充 + 熔断机制")
    print("=" * 50)

    # ========== 步骤2：产能计算 ==========
    daily_remaining = {day: MAX_DAILY_POMODOROS - consumed for day, consumed in daily_consumed.items()}
    total_remaining = sum(daily_remaining.values())

    print(f"\n📊 每日空槽（每日上限11番茄）:")
    for day in WEEKDAYS:
        print(f"   {day}: 已耗{daily_consumed[day]} → 剩余{daily_remaining[day]}空槽")
    print(f"   本周剩余总空槽: {total_remaining}番茄")

    # ========== 步骤3：动态填充 ==========
    task_parents = decompose_to_tasks(pain_points)
    dynamic_scheduled = []
    backlog_tasks = []

    print(f"\n🔍 动态任务拆解: {len(task_parents)}个")

    for parent in task_parents:
        children_pomos = sum(c.get("pomodoros", 1) for c in parent.get("children", []))
        parent_pomos = children_pomos if children_pomos > 0 else 1

        # 找第一个有足够槽的星期
        target_day = None
        for day in WEEKDAYS:
            if daily_remaining.get(day, 0) >= parent_pomos:
                target_day = day
                break

        if target_day:
            parent["date"] = get_weekday_date(target_day)
            parent["source"] = "dynamic"
            parent["pomodoros"] = parent_pomos
            daily_remaining[target_day] -= parent_pomos
            dynamic_scheduled.append(parent)
            print(f"  ✅ {parent['content']} → {target_day}({parent_pomos}番茄), 剩余{daily_remaining[target_day]}")
        else:
            # ========== 步骤4：熔断机制 ==========
            # 无足够槽，标记为下周 Backlog
            parent["source"] = "backlog"
            parent["pomodoros"] = parent_pomos
            parent["backlog_reason"] = "产能不足"
            backlog_tasks.append(parent)
            print(f"  🔴 [Backlog] {parent['content']} ({parent_pomos}番茄)")

    total_dynamic_pomos = sum(t.get("pomodoros", 0) for t in dynamic_scheduled)
    total_backlog_pomos = sum(t.get("pomodoros", 0) for t in backlog_tasks)

    print(f"\n📊 动态填充结果:")
    print(f"   已排期: {len(dynamic_scheduled)}个, {total_dynamic_pomos}番茄")
    print(f"   Backlog: {len(backlog_tasks)}个, {total_backlog_pomos}番茄")
    print(f"   消耗本周剩余空槽: {total_remaining - sum(daily_remaining.values())}番茄")

    return dynamic_scheduled, backlog_tasks, daily_remaining


def decompose_to_tasks(pain_points):
    """将痛点拆解为父子任务结构"""
    task_parents = []

    for pp in pain_points:
        content = pp.get("content", "")

        if is_forbidden(content):
            continue

        # 提取关键词判断任务类型
        if "早晨" in content or "早上" in content or "起床" in content:
            task_parents.append({
                "content": "[PAIN] 早晨效率困境-建立工作状态仪式",
                "priority": "p2",
                "children": [
                    {"content": "识别每日琐事清单并分类", "pomodoros": 1},
                    {"content": "设计3步入口仪式并测试", "pomodoros": 2},
                ]
            })
        elif "BGM" in content or "曲库" in content or "剪映" in content:
            task_parents.append({
                "content": "[PAIN] BGM曲库重建-建立抖音可搜曲库",
                "priority": "p2",
                "children": [
                    {"content": "研究抖音热门BGM并建立清单", "pomodoros": 2},
                    {"content": "在剪映验证BGM可搜性", "pomodoros": 1},
                ]
            })
        elif "腱鞘" in content or "康复" in content:
            task_parents.append({
                "content": "[PAIN] 腱鞘炎康复-搜索并执行康复动作",
                "priority": "p3",
                "children": [
                    {"content": "搜索腱鞘炎康复动作", "pomodoros": 1},
                    {"content": "制定康复计划并执行记录", "pomodoros": 1},
                ]
            })
        elif "Claude" in content or "GetNote" in content or "复盘" in content:
            task_parents.append({
                "content": "[KERNEL] Claude+GetNote联动-建立周复盘自动化",
                "priority": "p2",
                "children": [
                    {"content": "设计周复盘流程并文档化", "pomodoros": 2},
                    {"content": "编写GetNote提取脚本", "pomodoros": 3},
                ]
            })
        elif "CLI" in content or "小红书" in content or "知乎" in content:
            task_parents.append({
                "content": "[OPS] CLI工具-小红书抖音知乎批处理",
                "priority": "p3",
                "children": [
                    {"content": "研究各平台CLI方案", "pomodoros": 2},
                    {"content": "实现抖音创作者CLI工具", "pomodoros": 2},
                ]
            })

    # 去重
    seen = set()
    unique = []
    for p in task_parents:
        if p["content"] not in seen:
            seen.add(p["content"])
            unique.append(p)

    return unique

def is_forbidden(content):
    """检查是否包含禁止关键词"""
    content_lower = content.lower()
    forbidden = ["外包", "outsourcing", "手臂训练", "上肢训练", "健身房练臂"]
    return any(kw.lower() in content_lower for kw in forbidden)

# ============ 核心逻辑 ============

def extract_pain_goal_notes(days=7):
    """提取过去N天的 [PAIN]/[GOAL] 标签内容"""
    # 搜索痛点和目标相关的关键词
    queries = ["痛点", "目标", "计划", "问题", "困境", "康复"]
    all_notes = {}

    for query in queries:
        result = semantic_recall(query, limit=20)
        notes = result.get("data", {}).get("results", [])
        for note in notes:
            note_id = note.get("note_id")
            if note_id and note_id not in all_notes:
                all_notes[note_id] = note

    # 过滤7天内的笔记
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    recent_notes = []

    for note_id, note in all_notes.items():
        created_at = note.get("created_at", "")
        note_date = created_at.split(" ")[0] if created_at else ""
        if note_date >= cutoff:
            recent_notes.append(note)

    return recent_notes

def analyze_notes_to_tasks(notes=None):
    """分析笔记，提取痛点/目标，生成任务列表（带防重逻辑）"""
    # Step 1: 读取 sync_state
    sync_state = load_sync_state()
    print(f"📋 已处理笔记数: {len(sync_state.get('processed_note_ids', []))}")

    # 搜索查询词
    search_queries = [
        "每天 复盘 日记",
        "今天 计划 痛点",
        "早上 效率 工作状态",
        "康复 腱鞘炎 目标",
    ]

    all_pain_points = []
    all_note_ids = []
    seen_contents = set()

    for query in search_queries:
        result = semantic_recall(query, limit=10)
        notes_found = result.get("data", {}).get("results", [])
        for note in notes_found:
            note_id = note.get("note_id")
            content = note.get("content", "")
            # 防重：检查 sync_state
            if note_id in sync_state.get("processed_note_ids", []):
                continue
            # 去重
            content_hash = hash(content[:100])
            if content_hash not in seen_contents and len(content) > 20:
                seen_contents.add(content_hash)
                all_pain_points.append({
                    "content": content,
                    "created_at": note.get("created_at", ""),
                    "note_id": note_id
                })
                all_note_ids.append(note_id)

    print(f"🆕 新笔记数: {len(all_note_ids)}")

    # 返回新笔记ID供后续标记
    return all_pain_points, all_note_ids

def decompose_to_tasks(pain_points):
    """将痛点拆解为父子任务结构"""
    # 简单规则拆解（可后续接入LLM增强）
    task_parents = []

    for pp in pain_points:
        content = pp.get("content", "")

        if is_forbidden(content):
            continue

        # 提取关键词判断任务类型
        if "早晨" in content or "早上" in content or "起床" in content:
            parent = {
                "content": "[PAIN] 早晨效率困境-建立工作状态仪式",
                "date": get_weekday_date("Monday"),
                "priority": "p2",
                "children": [
                    {"content": "识别每日琐事清单并分类", "pomodoros": 1},
                    {"content": "设计3步入口仪式并测试", "pomodoros": 2},
                ]
            }
            task_parents.append(parent)

        if "BGM" in content or "曲库" in content or "剪映" in content:
            parent = {
                "content": "[PAIN] BGM曲库重建-建立抖音可搜曲库",
                "date": get_weekday_date("Monday", offset=1),
                "priority": "p2",
                "children": [
                    {"content": "研究抖音热门BGM并建立清单", "pomodoros": 2},
                    {"content": "在剪映验证BGM可搜性", "pomodoros": 1},
                ]
            }
            task_parents.append(parent)

        if "腱鞘" in content or "康复" in content:
            parent = {
                "content": "[PAIN] 腱鞘炎康复-搜索并执行康复动作",
                "date": get_weekday_date("Monday", offset=1),
                "priority": "p3",
                "children": [
                    {"content": "搜索腱鞘炎康复动作", "pomodoros": 1},
                    {"content": "制定康复计划并执行记录", "pomodoros": 1},
                ]
            }
            task_parents.append(parent)

        if "Claude" in content or "GetNote" in content or "复盘" in content:
            parent = {
                "content": "[KERNEL] Claude+GetNote联动-建立周复盘自动化",
                "date": get_weekday_date("Monday", offset=2),
                "priority": "p2",
                "children": [
                    {"content": "设计周复盘流程并文档化", "pomodoros": 2},
                    {"content": "编写GetNote提取脚本", "pomodoros": 3},
                ]
            }
            task_parents.append(parent)

        if "CLI" in content or "小红书" in content or "知乎" in content:
            parent = {
                "content": "[OPS] CLI工具-小红书抖音知乎批处理",
                "date": get_weekday_date("Monday", offset=3),
                "priority": "p3",
                "children": [
                    {"content": "研究各平台CLI方案", "pomodoros": 2},
                    {"content": "实现抖音创作者CLI工具", "pomodoros": 2},
                ]
            }
            task_parents.append(parent)

    # 去重
    seen = set()
    unique_parents = []
    for p in task_parents:
        if p["content"] not in seen:
            seen.add(p["content"])
            unique_parents.append(p)

    return unique_parents

def get_weekday_date(weekday_name, offset=0):
    """获取下一个指定星期X的日期"""
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    target_day = weekdays.index(weekday_name)

    today = datetime.now()
    days_ahead = target_day - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    days_ahead += offset * 7

    next_date = today + timedelta(days=days_ahead)
    return next_date.strftime("%Y-%m-%d")

def create_tasks_in_todoist(task_parents, note_ids=None):
    """创建任务到 Todoist，成功后更新 sync_state"""
    created = []
    sync_state = load_sync_state()

    for parent in task_parents:
        # 创建父任务
        p = add_task(
            content=parent["content"],
            date=parent["date"],
            priority=parent["priority"]
        )
        parent_id = p.get("id")
        print(f"已添加父任务: {parent['content']} (ID: {parent_id})")

        # 创建子任务
        for child in parent.get("children", []):
            if is_forbidden(child["content"]):
                continue
            c = add_task(
                content=child["content"],
                date=parent["date"],
                priority=parent["priority"],
                parent_id=parent_id
            )
            print(f"  └─ 子任务: {child['content']} ({child['pomodoros']}番茄)")

        created.append({
            "parent": parent,
            "parent_id": parent_id
        })

    # 更新 sync_state
    if note_ids:
        mark_notes_processed(note_ids, sync_state)

    return created

def generate_weekly_report(task_parents):
    """生成周计划报告"""
    print("\n" + "="*60)
    print("📋 下周产能装箱报告")
    print("="*60)
    print(f"日期范围: {get_weekday_date('Monday')} ~ {get_weekday_date('Sunday', offset=0)}")
    print(f"总番茄产能: 66番茄/周")
    print()

    total_pomodoros = 0
    for i, parent in enumerate(task_parents, 1):
        children_pomos = sum(c.get("pomodoros", 1) for c in parent.get("children", []))
        total_pomodoros += children_pomos

        print(f"### {i}. {parent['content']}")
        print(f"   日期: {parent['date']} | 优先级: {parent['priority']} | 番茄数: {children_pomos}")
        for child in parent.get("children", []):
            print(f"   - {child['content']} ({child.get('pomodoros', 1)}番茄)")
        print()

    print(f"**总预估番茄**: {total_pomodoros}/66")
    print(f"**剩余产能**: {66 - total_pomodoros}番茄")
    print()

# ============ 主流程 ============

def main():
    """
    四步执行流程:
    1. 基线锁仓: weekly_baseline.json → Todoist
    2. 产能计算: 计算每日剩余空槽
    3. 动态填充: GetNote新笔记 → 剩余空槽
    4. 熔断机制: 超额任务 → Backlog
    """
    print("🚀 周计划生成器 - 四步调度模式")
    print(f"日期范围: {get_weekday_date('Monday')} ~ {get_weekday_date('Sunday')}")
    print()

    # ========== 步骤1：基线锁仓 ==========
    baseline_tasks, daily_consumed, baseline_pomos = schedule_baseline_tasks()

    # ========== 步骤2+3+4：动态填充 + 熔断 ==========
    pain_points, note_ids = analyze_notes_to_tasks()
    print(f"✅ 发现 {len(pain_points)} 条新痛点/目标")
    dynamic_tasks, backlog_tasks, daily_remaining = schedule_dynamic_tasks(pain_points, daily_consumed)

    # ========== 生成报告 ==========
    print("\n" + "=" * 60)
    print("📋 下周产能装箱报告")
    print("=" * 60)

    print("\n### 基线任务（已锁仓）")
    for task in baseline_tasks:
        print(f"  📌 {task['date']} | {task['content']} ({task['pomodoros']}番茄)")

    print("\n### 动态填充")
    for task in dynamic_tasks:
        print(f"  🔄 {task['date']} | {task['content']} ({task['pomodoros']}番茄)")

    if backlog_tasks:
        print("\n### 🔴 Backlog（下周积压）")
        for task in backlog_tasks:
            print(f"  ⏳ {task['content']} ({task['pomodoros']}番茄) - {task['backlog_reason']}")

    total_dynamic = sum(t.get("pomodoros", 0) for t in dynamic_tasks)
    total_backlog = sum(t.get("pomodoros", 0) for t in backlog_tasks)

    print("\n" + "-" * 40)
    print(f"📊 基线: {baseline_pomos}番茄 ({len(baseline_tasks)}个任务)")
    print(f"📊 动态: {total_dynamic}番茄 ({len(dynamic_tasks)}个任务)")
    print(f"📊 Backlog: {total_backlog}番茄 ({len(backlog_tasks)}个任务)")
    print(f"📊 本周已用: {baseline_pomos + total_dynamic}番茄 / 66番茄")
    print(f"📊 剩余产能: {66 - baseline_pomos - total_dynamic}番茄")

    # ========== 确认后创建 ==========
    print("\n是否创建任务到 Todoist? (y/n)")
    response = input()

    if response.lower() == 'y':
        if baseline_tasks:
            create_tasks_in_todoist(baseline_tasks, note_ids=None)
        if dynamic_tasks:
            create_tasks_in_todoist(dynamic_tasks, note_ids=note_ids)
        print("\n✅ 任务已创建到 Todoist（Backlog 任务仅报告，不写入）")
    else:
        print("\n⚠️ 任务未创建")

if __name__ == "__main__":
    # 直接运行 main() 双轨流程
    main()
