#!/usr/bin/env python3
"""
番茄ToDo CLI Tool
管理番茄工作法的待办事项和记录
"""

import json
import sys
import os
import io
from pathlib import Path
from datetime import datetime

# 修复 Windows 控制台中文显示
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置
DATA_DIR = Path.home() / "AppData" / "Roaming" / "番茄ToDo"
DB_FILE = DATA_DIR / "tomatodo_db.json"

# 颜色
def c(msg, color=''):
    """带颜色的打印"""
    colors = {
        'r': '\033[91m', 'g': '\033[92m', 'y': '\033[93m',
        'b': '\033[94m', 'c': '\033[96m', '': '\033[0m'
    }
    return f"{colors.get(color, '')}{msg}{colors['']}"


def load_db():
    """加载数据库"""
    if not DB_FILE.exists():
        print(f"[ERROR] Database not found: {DB_FILE}")
        sys.exit(1)
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_db(data):
    """保存数据库"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_todos(data, show_completed=False):
    """列出待办事项"""
    todos = data.get('PCToDo', [])

    active = [t for t in todos if t.get('isComplied', 0) == 0]
    completed = [t for t in todos if t.get('isComplied', 0) > 0]

    print(f"\n{c('=== 番茄ToDo 待办事项 ===', 'c')}\n")

    if active:
        print(c(f"待完成 ({len(active)})", 'y'))
        for t in active:
            name = t.get('name', 'Unknown')
            time = t.get('time', 25)
            cat = t.get('s1', '')
            tid = t.get('id', 0)
            print(f"  [{tid}] {name} ({time}分钟)")
            if cat:
                print(f"       分类: {cat}")
    else:
        print(c("没有待完成的事项", 'g'))

    if show_completed and completed:
        print(f"\n{c(f'已完成 ({len(completed)})', 'g')}")
        for t in completed[:10]:  # 只显示前10个
            name = t.get('name', 'Unknown')
            count = t.get('isComplied', 0)
            print(f"  [{count}x] {name}")
        if len(completed) > 10:
            print(f"  ... 还有 {len(completed) - 10} 项")

    print()


def add_todo(name, time=25, category=''):
    """添加待办事项"""
    data = load_db()
    todos = data.get('PCToDo', [])

    # 获取下一个ID
    max_id = max([t.get('id', 0) for t in todos], default=0)

    new_todo = {
        'id': max_id + 1,
        'name': name,
        'originalName': name,
        'time': time,
        'isComplied': 0,
        'repeatMode': 0,
        'i1': 0, 'i2': 0, 'i3': 0, 'i4': 0, 'i5': 0,
        'i6': 0, 'i7': 0, 'i8': 0, 'i9': 0,
        's1': category,
        's2': str(int(datetime.now().timestamp() * 1000)),
        's3': '',
        's4': '',
        's5': ' 分钟',
        's6': '', 's7': '', 's8': '', 's9': '',
        'type': 0,
        'situation': 0,
        'sourceType': 'pc',
        'phoneId': 0,
        'isSynced': 0
    }

    todos.append(new_todo)
    data['PCToDo'] = todos

    # 更新计数器
    data['todoIdCounter'] = max_id + 1

    save_db(data)
    print(f"[OK] Added: {name} ({time}分钟)")
    if category:
        print(f"     分类: {category}")


def complete_todo(todo_id):
    """完成一个待办（增加完成计数）"""
    data = load_db()
    todos = data.get('PCToDo', [])

    for t in todos:
        if t.get('id') == todo_id:
            t['isComplied'] = t.get('isComplied', 0) + 1
            t['isSynced'] = 0
            save_db(data)
            print(f"[OK] Completed: {t.get('name')} (已完成的番茄数: {t['isComplied']})")
            return

    print(f"[ERROR] Todo {todo_id} not found")


def delete_todo(todo_id):
    """删除待办事项"""
    data = load_db()
    todos = data.get('PCToDo', [])

    for i, t in enumerate(todos):
        if t.get('id') == todo_id:
            name = t.get('name')
            todos.pop(i)
            data['PCToDo'] = todos
            save_db(data)
            print(f"[OK] Deleted: {name}")
            return

    print(f"[ERROR] Todo {todo_id} not found")


def reset_todo(todo_id):
    """重置待办为未完成"""
    data = load_db()
    todos = data.get('PCToDo', [])

    for t in todos:
        if t.get('id') == todo_id:
            t['isComplied'] = 0
            t['isSynced'] = 0
            save_db(data)
            print(f"[OK] Reset: {t.get('name')}")
            return

    print(f"[ERROR] Todo {todo_id} not found")


def show_stats(data):
    """显示统计信息"""
    todos = data.get('PCToDo', [])
    records = data.get('PCRecord', [])

    active = [t for t in todos if t.get('isComplied', 0) == 0]
    completed = [t for t in todos if t.get('isComplied', 0) > 0]

    total_pomodoros = sum([t.get('isComplied', 0) for t in todos])
    total_time = sum([t.get('time', 25) * t.get('isComplied', 0) for t in todos])

    # 今天的记录
    today = datetime.now().strftime('%Y-%m-%d')
    today_records = [r for r in records if
                     datetime.fromtimestamp(r.get('startDate', 0)/1000).strftime('%Y-%m-%d') == today]

    print(f"\n{c('=== 番茄ToDo 统计 ===', 'c')}\n")
    print(f"  待完成事项: {len(active)}")
    print(f"  已完成事项: {len(completed)}")
    print(f"  总番茄数:   {total_pomodoros}")
    print(f"  总时间:    {total_time} 分钟 ({total_time/60:.1f} 小时)")
    print(f"  今日番茄:  {len(today_records)}")

    # 按时段统计
    if records:
        print(f"\n{c('最近活动:', 'y')}")
        recent = sorted(records, key=lambda x: x.get('createDate', 0), reverse=True)[:5]
        for r in recent:
            ts = datetime.fromtimestamp(r.get('createDate', 0)/1000)
            print(f"  {ts.strftime('%m-%d %H:%M')} - {r.get('name', 'Unknown')} ({r.get('time', 25)}分钟)")


def import_tasks(task_list):
    """批量导入任务，自动计算番茄数

    task_list: [(名称, 预计总时间分钟), ...]
    """
    data = load_db()
    todos = data.get('PCToDo', [])
    max_id = max([t.get('id', 0) for t in todos], default=0)

    # 每个番茄25分钟工作 + 5分钟休息 = 30分钟周期
    CYCLE_MINUTES = 30

    print(f"\n{c('=== 导入任务预览 ===', 'c')}\n")
    print(f"{'名称':<30} {'预计时间':>10} {'番茄数':>8} {'工作+休息':>12}")
    print("-" * 65)

    total_pomodoros = 0
    for name, total_minutes in task_list:
        pomodoros = (total_minutes + CYCLE_MINUTES - 1) // CYCLE_MINUTES  # 向上取整
        total_pomodoros += pomodoros
        work_time = pomodoros * 25
        rest_time = pomodoros * 5
        print(f"{name:<30} {total_minutes:>7}分钟 {pomodoros:>6}个   {work_time}分钟+{rest_time}分钟")

    print("-" * 65)
    total_minutes = sum(t for _, t in task_list)
    total_work = total_pomodoros * 25
    total_rest = total_pomodoros * 5
    print(f"{'合计':<30} {total_minutes:>7}分钟 {total_pomodoros:>6}个   {total_work}分钟+{total_rest}分钟")
    print()
    print(f"说明: 每个番茄 = 25分钟工作 + 5分钟休息 = 30分钟")
    print()

    # 确认导入
    confirm = input(f"确认导入 {len(task_list)} 个任务? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return

    # 执行导入
    for name, total_minutes in task_list:
        pomodoros = (total_minutes + 24) // 25
        max_id += 1

        new_todo = {
            'id': max_id,
            'name': name,
            'originalName': name,
            'time': 25,  # 每个番茄25分钟
            'isComplied': 0,
            'repeatMode': 0,
            'i1': 0, 'i2': 0, 'i3': 0, 'i4': 0, 'i5': pomodoros,  # i5 存放下次番茄数
            'i6': 0, 'i7': 0, 'i8': 0, 'i9': 0,
            's1': '',
            's2': str(int(datetime.now().timestamp() * 1000)),
            's3': '',
            's4': '',
            's5': ' 分钟',
            's6': '', 's7': '', 's8': '', 's9': '',
            'type': 0,
            'situation': 0,
            'sourceType': 'pc',
            'phoneId': 0,
            'isSynced': 0
        }
        todos.append(new_todo)
        print(f"[OK] {name}: 需要 {pomodoros} 个番茄")

    data['PCToDo'] = todos
    data['todoIdCounter'] = max_id
    save_db(data)

    total_work = total_pomodoros * 25
    total_rest = total_pomodoros * 5
    print(f"\n[OK] 已导入 {len(task_list)} 个任务")
    print(f"     共计 {total_pomodoros} 个番茄 ({total_work}分钟工作 + {total_rest}分钟休息)")


def show_records(data, limit=10):
    """显示番茄记录"""
    records = data.get('PCRecord', [])

    if not records:
        print(c("没有番茄记录", 'y'))
        return

    # 按时间排序
    sorted_records = sorted(records, key=lambda x: x.get('createDate', 0), reverse=True)[:limit]

    print(f"\n{c('=== 番茄记录 ===', 'c')}\n")
    for r in sorted_records:
        ts = datetime.fromtimestamp(r.get('createDate', 0)/1000)
        name = r.get('name', 'Unknown')
        time = r.get('time', 25)
        complete = r.get('isComplete', 0)
        status = c('完成', 'g') if complete else c('中断', 'r')
        print(f"  {ts.strftime('%m-%d %H:%M')} {name:<20} {time}分钟 [{status}]")


def show_help():
    """显示帮助"""
    print(f"""
{c('番茄ToDo CLI', 'c')}

{c('用法:', 'y')}
  python tomato_cli.py <命令> [参数]

{c('命令:', 'y')}
  list, ls              列出待办事项
  add <名称> [分钟]     添加待办事项（默认25分钟）
  done <ID>             完成一个待办（增加番茄计数）
  delete <ID>           删除待办事项
  reset <ID>            重置待办为未完成
  stats                 显示统计信息
  records [数量]        显示番茄记录（默认10条）
  import "名称,分钟"    批量导入任务，自动计算番茄数
  help                  显示帮助

{c('示例:', 'y')}
  python tomato_cli.py list
  python tomato_cli.py add "写代码" 30
  python tomato_cli.py add "读书" 25 工作
  python tomato_cli.py done 1
  python tomato_cli.py delete 2
  python tomato_cli.py stats
  python tomato_cli.py records
  python tomato_cli.py import "写代码,60" "读书,30" "开会,45"
""")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'

    if cmd in ('help', '-h', '--help'):
        show_help()

    elif cmd in ('list', 'ls'):
        data = load_db()
        show_completed = '--all' in sys.argv or '-a' in sys.argv
        list_todos(data, show_completed)

    elif cmd == 'add':
        if len(sys.argv) < 3:
            print("[ERROR] Usage: add <名称> [时间(分钟)] [分类]")
        else:
            name = sys.argv[2]
            time = int(sys.argv[3]) if len(sys.argv) > 3 else 25
            category = sys.argv[4] if len(sys.argv) > 4 else ''
            add_todo(name, time, category)

    elif cmd == 'done':
        if len(sys.argv) < 3:
            print("[ERROR] Usage: done <ID>")
        else:
            complete_todo(int(sys.argv[2]))

    elif cmd == 'delete':
        if len(sys.argv) < 3:
            print("[ERROR] Usage: delete <ID>")
        else:
            delete_todo(int(sys.argv[2]))

    elif cmd == 'reset':
        if len(sys.argv) < 3:
            print("[ERROR] Usage: reset <ID>")
        else:
            reset_todo(int(sys.argv[2]))

    elif cmd == 'stats':
        data = load_db()
        show_stats(data)

    elif cmd == 'records':
        data = load_db()
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_records(data, limit)

    elif cmd == 'import':
        # 批量导入任务: import "任务1,60" "任务2,30"
        # 格式: "名称,预计分钟数"
        tasks = []
        for arg in sys.argv[2:]:
            if ',' in arg:
                name, minutes = arg.rsplit(',', 1)
                tasks.append((name.strip(), int(minutes.strip())))
            else:
                tasks.append((arg, 25))  # 默认25分钟
        if tasks:
            import_tasks(tasks)
        else:
            print("[ERROR] Usage: import \"任务名,分钟数\" ...")

    else:
        print(f"[ERROR] Unknown command: {cmd}")
        show_help()
