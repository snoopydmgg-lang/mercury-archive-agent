"""
极简习惯追踪器
用法:
  python habit_tracker.py log <习惯名> [备注]
  python habit_tracker.py list [习惯名]
  python habit_tracker.py stats [习惯名]

示例:
  python habit_tracker.py log 戒手机
  python habit_tracker.py log 戒手机 --note "下午开会无聊刷了5分钟"
  python habit_tracker.py list 戒手机
  python habit_tracker.py stats
"""

import csv
import sys
import os
from datetime import datetime, date
from pathlib import Path

# ========== 配置 ==========
DATA_DIR = Path(__file__).parent / "habit_data"
DATA_FILE = DATA_DIR / "habits.csv"
CONFIG_FILE = DATA_DIR / "habits.csv.config"

# ========== 初始化 ==========
DATA_DIR.mkdir(exist_ok=True)
if not DATA_FILE.exists():
    DATA_FILE.write_text("date,time,habit,note\n", encoding="utf-8")


def log(habit: str, note: str = ""):
    """记录一次打卡"""
    now = datetime.now()
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            habit.strip(),
            note.strip()
        ])
    print(f"  [LOGGED] {now.strftime('%H:%M')} {habit}")


def list_habits(target: str = ""):
    """列出打卡记录"""
    rows = []
    with open(DATA_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if target and target.lower() not in row["habit"].lower():
                continue
            rows.append(row)

    if not rows:
        print("  无记录")
        return

    # 按习惯分组显示
    habits = {}
    for row in rows:
        h = row["habit"]
        if h not in habits:
            habits[h] = []
        habits[h].append(row)

    for h, entries in habits.items():
        print(f"\n  ## {h} ({len(entries)}次)")
        # 只显示最近10条
        for row in entries[-10:][::-1]:
            print(f"    {row['date']} {row['time']}  {row['note']}")


def stats(target: str = ""):
    """统计"""
    counts = {}
    with open(DATA_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if target and target.lower() not in row["habit"].lower():
                continue
            h = row["habit"]
            counts[h] = counts.get(h, 0) + 1

    if not counts:
        print("  无数据")
        return

    print("\n  习惯统计")
    print("  " + "-" * 30)
    for h, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {h:<20} {c:>4}次")

    # 连续天数
    today = date.today()
    print("\n  连续打卡（最近30天）")
    print("  " + "-" * 30)
    for h in counts:
        streak = 0
        check = today
        habit_dates = set()
        with open(DATA_FILE, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["habit"] == h:
                    habit_dates.add(row["date"])
        for i in range(30):
            d = (check - __import__('datetime').timedelta(days=i)).isoformat()
            if d in habit_dates:
                streak += 1
            else:
                break
        print(f"    {h:<20} {streak:>3}天")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "log":
        habit = sys.argv[2] if len(sys.argv) > 2 else input("习惯名: ")
        note = ""
        for i, arg in enumerate(sys.argv):
            if arg == "--note" and i + 1 < len(sys.argv):
                note = sys.argv[i + 1]
                break
        log(habit, note)

    elif cmd == "list":
        target = sys.argv[2] if len(sys.argv) > 2 else ""
        list_habits(target)

    elif cmd == "stats":
        target = sys.argv[2] if len(sys.argv) > 2 else ""
        stats(target)

    else:
        print(__doc__)
