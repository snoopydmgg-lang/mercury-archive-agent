"""
ICS日历文件生成器
用于生成可以导入手机的日历提醒
"""

import os
from datetime import datetime, timedelta

def create_simple_ics_event(
    title: str,
    description: str = "",
    start_datetime: str = None,  # 格式: "20260320T100000"
    duration_minutes: int = 60,
    location: str = "",
    reminder_minutes: int = 30
) -> str:
    """
    创建单个ICS事件（简化版）
    """

    # 解析时间
    if start_datetime:
        # 已经是ICS格式
        start = start_datetime
    else:
        # 使用当前时间
        dt = datetime.now() + timedelta(hours=1)
        start = dt.strftime("%Y%m%dT%H%M%S")

    # 计算结束时间
    dt_start = datetime.strptime(start, "%Y%m%dT%H%M%S")
    dt_end = dt_start + timedelta(minutes=duration_minutes)
    end = dt_end.strftime("%Y%m%dT%H%M%S")

    # 创建VALARM提醒
    alarm_trigger = f"-PT{reminder_minutes}M"  # 如 -PT30M 表示提前30分钟

    ics_content = f"""BEGIN:VEVENT
DTSTART:{start}
DTEND:{end}
DTSTAMP:{datetime.now().strftime("%Y%m%dT%H%M%S")}
UID:{datetime.now().strftime("%Y%m%d%H%M%S")}@shuixing.com
SUMMARY:{title}
DESCRIPTION:{description}
LOCATION:{location}
BEGIN:VALARM
TRIGGER:{alarm_trigger}
ACTION:DISPLAY
DESCRIPTION:提醒: {title}
END:VALARM
END:VEVENT"""

    return ics_content

def create_ics_calendar(events: list, output_file: str = "schedule.ics"):
    """
    创建ICS日历文件（多事件）
    """
    # 头部
    header = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//水星艺术馆//日程//ZH-CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    # 尾部
    footer = ["END:VCALENDAR"]

    # 合并
    all_lines = header + events + footer

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_lines))

    return output_file

def quick_add(
    title: str,
    description: str = "",
    days_later: int = 0,
    hour: int = 14,
    minute: int = 0,
    duration: int = 60,
    reminder: int = 30
) -> str:
    """
    快速添加日程

    参数:
        title: 标题
        description: 描述
        days_later: 几天后
        hour: 小时
        minute: 分钟
        duration: 持续分钟
        reminder: 提醒提前分钟
    """
    start_time = datetime.now() + timedelta(days=days_later)
    start_time = start_time.replace(hour=hour, minute=minute, second=0)

    start_str = start_time.strftime("%Y%m%dT%H%M%S")

    event = create_simple_ics_event(
        title=title,
        description=description,
        start_datetime=start_str,
        duration_minutes=duration,
        reminder_minutes=reminder
    )

    return event

# ============== 命令行接口 ==============

def main():
    import sys

    print("=" * 50)
    print("ICS日历生成器")
    print("=" * 50)

    if len(sys.argv) < 3:
        print("\n用法:")
        print("  python ics_generator.py <标题> <日期> [时间] [时长] [提醒]")
        print("\n示例:")
        print('  python ics_generator.py "复盘会议" "2026-03-20" "17:00" 60 30')
        print("\n参数说明:")
        print("  标题: 事件名称")
        print("  日期: YYYY-MM-DD 格式")
        print("  时间: HH:MM 格式 (默认 14:00)")
        print("  时长: 分钟数 (默认 60)")
        print("  提醒: 提前分钟数 (默认 30)")
        return

    title = sys.argv[1]
    date_str = sys.argv[2]  # "2026-03-20"
    time_str = sys.argv[3] if len(sys.argv) > 3 else "14:00"
    duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    reminder = int(sys.argv[5]) if len(sys.argv) > 5 else 30

    # 组合日期时间
    start_str = f"{date_str.replace('-','')}T{time_str.replace(':','')}00"

    # 解析用于描述
    description = " ".join(sys.argv[6:]) if len(sys.argv) > 6 else ""

    # 生成ICS
    event = create_simple_ics_event(
        title=title,
        description=description,
        start_datetime=start_str,
        duration_minutes=duration,
        reminder_minutes=reminder
    )

    # 生成文件名（默认输出到收件箱）
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:20]
    output_file = f"E:/1.work/douyin/1.shuixing/00_InBox_收件箱/{safe_title}.ics"

    create_ics_calendar([event], output_file)

    print(f"\n已生成: {output_file}")
    print(f"标题: {title}")
    print(f"时间: {date_str} {time_str}")
    print(f"时长: {duration} 分钟")
    print(f"提醒: 提前 {reminder} 分钟")

if __name__ == "__main__":
    main()
