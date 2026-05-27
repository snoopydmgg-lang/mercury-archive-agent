#!/usr/bin/env python3
"""OpenCode Token HUD - reads from OpenCode SQLite database.

Default mode: HUD progress bar dashboard.
Modes: --hud (default), --compact, --detail, --json, --session, --today, --month
"""

import sqlite3
import json
import os
import sys
import io
import calendar
from datetime import datetime, date, timezone, timedelta
from pathlib import Path

# Windows terminal UTF-8 encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ══════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════

DB_PATH = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
USD_TO_RMB = 7.2
CST = timezone(timedelta(hours=8))

# Budget defaults (RMB)
DAILY_BUDGET = 10.00
MONTHLY_BUDGET = 200.00

# Session thresholds
SESSION_LARGE_THRESHOLD = 10_000_000  # 10M tokens
SESSION_WARN_THRESHOLD = 5_000_000    # 5M tokens


# ══════════════════════════════════════════════════════════
#  Formatting utilities
# ══════════════════════════════════════════════════════════

def format_tokens(n):
    """Format token count with K/M suffix."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.0f}K"
    else:
        return str(n)


def format_rmb(usd):
    """Format USD as RMB string."""
    rmb = usd * USD_TO_RMB
    if rmb < 0.01:
        return "0.00"
    return f"{rmb:.2f}"


def parse_model(model_json):
    """Parse model JSON string to provider/model display."""
    if not model_json:
        return "unknown"
    try:
        m = json.loads(model_json)
        provider = m.get("providerID", "?")
        mid = m.get("id", "?")
        return f"{provider}/{mid}"
    except (json.JSONDecodeError, TypeError):
        return str(model_json)[:30]


# ══════════════════════════════════════════════════════════
#  Mercury Archive theme  (ANSI truecolor)
# ══════════════════════════════════════════════════════════

ACCENT = '\033[38;2;211;107;77m'       # #D36B4D
SECONDARY = '\033[38;2;230;200;181m'    # #E6C8B5
WARM_GRAY = '\033[38;2;138;133;128m'    # #8A8580
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'

_colors_active = True

THEME = {
    "title": "MERCURY TOKEN ARCHIVE",
    "subtitle": "CURATED USAGE LEDGER",
    "footer": "MERCURY ARCHIVE",
    "accent": ACCENT,
    "muted": WARM_GRAY,
    "soft": SECONDARY,
    "dim": DIM,
    "bold": BOLD,
    "reset": RESET,
    "width": 56,
    "progress": 24,       # progress bar fixed width
    "line": "\u2500",     # ─
    "fill": "\u2501",     # ━
    "pointer": "\u257a",  # ╺
}


def disable_colors():
    global _colors_active
    _colors_active = False


def c(code):
    return code if _colors_active else ''


def t(key):
    """Access theme value."""
    return THEME.get(key, '')


# ══════════════════════════════════════════════════════════
#  Progress bar functions
# ══════════════════════════════════════════════════════════

def thin_bar(value, max_value):
    """Fixed-width Mercury thin-line bar:  ━━━╺━━━━━━━━━━━━━━━  20%
    Filled segment in accent, unfilled in dim gray, pointer at boundary.
    Always t('progress') chars wide."""
    width = t('progress')
    ratio = value / max_value if max_value > 0 else 0
    ratio = min(ratio, 1.0)
    filled = int(ratio * width)

    fg = c(t('accent'))
    mg = c(t('dim'))
    r = c(RESET)
    fill_char = t('fill')      # ━
    ptr_char = t('pointer')     # ╺
    empty_char = t('fill')      # ━ (same char, dimmed)

    if filled == width:
        return f'{fg}{fill_char * width}{r}'
    if filled == 0:
        return f'{fg}{ptr_char}{mg}{empty_char * (width - 1)}{r}'
    return f'{fg}{fill_char * filled}{ptr_char}{mg}{empty_char * (width - filled - 1)}{r}'


def pct_str(value, max_value):
    ratio = value / max_value if max_value > 0 else 0
    ratio = min(ratio, 1.0)
    return f'{ratio * 100:.0f}%'.rjust(4)


def pad_col(text, width):
    """Pad text to fixed column width. Handles ANSI-stripped lengths."""
    clean = text.replace('\033[0m', '').replace('\033[2m', '')
    for code in [ACCENT, WARM_GRAY, SECONDARY, DIM, BOLD, RESET]:
        clean = clean.replace(code, '')
    visible = len(clean)
    return text + ' ' * max(0, width - visible)


def threshold_marker(ratio):
    if ratio > 0.8:
        return f'{c(t("accent"))}CRITICAL{c(RESET)}'
    elif ratio > 0.5:
        return f'{c(t("muted"))}WARNING{c(RESET)}'
    else:
        return f'{c(t("dim"))}OK{c(RESET)}'


def cache_status_label(rate):
    if rate >= 90:
        return f'{c(t("dim"))}excellent{c(RESET)}'
    elif rate >= 70:
        return f'{c(t("muted"))}good{c(RESET)}'
    else:
        return f'{c(t("accent"))}low{c(RESET)}'


def sep_line():
    """Full-width separator line in dim."""
    return f'{c(t("dim"))}{t("line") * t("width")}{c(RESET)}'


def section_label(name):
    """Bold accent section header."""
    return f'{c(t("bold"))}{c(t("accent"))}{name}{c(RESET)}'


# ══════════════════════════════════════════════════════════
#  Database queries
# ══════════════════════════════════════════════════════════

def get_sessions(conn, where_clause="", params=(), limit=None):
    """Query sessions with optional where clause."""
    limit_clause = f"LIMIT {limit}" if limit else ""
    sql = f"""
        SELECT id, title, model, cost,
               tokens_input, tokens_output, tokens_reasoning,
               tokens_cache_read, tokens_cache_write,
               time_created, time_updated
        FROM session
        {where_clause}
        ORDER BY time_created DESC
        {limit_clause}
    """
    cur = conn.cursor()
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def aggregate(sessions):
    """Aggregate token stats from a list of session dicts."""
    total_input = sum(s["tokens_input"] or 0 for s in sessions)
    total_output = sum(s["tokens_output"] or 0 for s in sessions)
    total_reasoning = sum(s["tokens_reasoning"] or 0 for s in sessions)
    total_cache_read = sum(s["tokens_cache_read"] or 0 for s in sessions)
    total_cache_write = sum(s["tokens_cache_write"] or 0 for s in sessions)
    total_cost = sum(s["cost"] or 0 for s in sessions)
    total_tokens = total_input + total_output + total_reasoning
    return {
        "count": len(sessions),
        "input": total_input,
        "output": total_output,
        "reasoning": total_reasoning,
        "cache_read": total_cache_read,
        "cache_write": total_cache_write,
        "cost_usd": total_cost,
        "total": total_tokens,
    }


def cache_hit_rate(cache_read, input_tokens, cache_write=0):
    """Calculate cache hit rate percentage."""
    denom = input_tokens + cache_write + cache_read
    if denom == 0:
        return 0
    return cache_read / denom * 100


# ══════════════════════════════════════════════════════════
#  Anomaly detection & suggestions
# ══════════════════════════════════════════════════════════

def detect_anomalies(sessions, large_threshold=SESSION_LARGE_THRESHOLD):
    """Detect anomalous sessions."""
    results = []
    for s in sessions:
        tags = []
        total = (s["tokens_input"] or 0) + (s["tokens_output"] or 0) + (s["tokens_reasoning"] or 0)
        if total > large_threshold:
            tags.append('large')
        input_like = (s["tokens_input"] or 0) + (s["tokens_cache_read"] or 0) + (s["tokens_cache_write"] or 0)
        s_cache_rate = ((s["tokens_cache_read"] or 0) / input_like * 100) if input_like > 0 else 0
        if s_cache_rate < 30 and input_like > 1_000_000:
            tags.append('low_cache')
        if tags:
            results.append((s, tags))
    return results


def generate_suggestions(cache_hit_rate_pct, today_tokens, recent_sessions, month_session_count):
    """Generate usage suggestions."""
    suggestions = []
    if cache_hit_rate_pct >= 90:
        suggestions.append(('good', 'Cache hit rate excellent, good context reuse'))
    elif cache_hit_rate_pct < 70:
        suggestions.append(('warn', 'Cache hit rate low - frequent new sessions or large context changes'))

    anomalies = detect_anomalies(recent_sessions[:10])
    large_count = sum(1 for _, tags in anomalies if 'large' in tags)
    lowc_count = sum(1 for _, tags in anomalies if 'low_cache' in tags)
    if large_count > 0:
        suggestions.append(('warn', f'{large_count} session(s) exceed 10M tokens, check task splitting'))
    if lowc_count > 0:
        suggestions.append(('warn', f'{lowc_count} session(s) cache rate <30%, high new-session cost'))
    if today_tokens > 100_000_000:
        suggestions.append(('warn', 'High daily usage (>100M), check for abnormal sessions'))
    if month_session_count > 100:
        suggestions.append(('info', f'{month_session_count} sessions this month, frequent new sessions reduce cache efficiency'))

    if not suggestions:
        suggestions.append(('good', 'All metrics normal'))
    return suggestions


# ══════════════════════════════════════════════════════════
#  EOM projection
# ══════════════════════════════════════════════════════════

def compute_eom(month_cost_usd, days_elapsed, days_in_month):
    """Compute end-of-month cost projection."""
    if days_elapsed <= 0:
        return 0
    daily_avg = month_cost_usd / days_elapsed
    return daily_avg * days_in_month


# ══════════════════════════════════════════════════════════
#  Build dashboard data
# ══════════════════════════════════════════════════════════

def build_dashboard_data(conn):
    """Build all dashboard data from OpenCode SQLite."""
    now = datetime.now(CST)
    today = now.date()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    today_ts = int(today_start.timestamp() * 1000)
    month_ts = int(month_start.timestamp() * 1000)

    all_sessions = get_sessions(conn)
    if not all_sessions:
        return None

    # Current session = most recent
    current = all_sessions[0]
    today_sessions = [s for s in all_sessions if (s["time_created"] or 0) >= today_ts]
    month_sessions = [s for s in all_sessions if (s["time_created"] or 0) >= month_ts]

    # Aggregates
    current_stats = aggregate([current])
    today_stats = aggregate(today_sessions)
    month_stats = aggregate(month_sessions)
    all_stats = aggregate(all_sessions)

    # Cache hit rates
    month_cache_rate = cache_hit_rate(
        month_stats["cache_read"], month_stats["input"], month_stats["cache_write"]
    )
    today_cache_rate = cache_hit_rate(
        today_stats["cache_read"], today_stats["input"], today_stats["cache_write"]
    )

    # EOM projection
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    eom_usd = compute_eom(month_stats["cost_usd"], days_elapsed, days_in_month)

    # Model
    model = parse_model(current["model"])

    # Recent 5 sessions
    recent_5 = all_sessions[:5]

    # Suggestions
    suggestions = generate_suggestions(
        month_cache_rate,
        today_stats["total"],
        recent_5,
        month_stats["count"],
    )

    return {
        "now": now,
        "model": model,
        "current": current_stats,
        "today": today_stats,
        "month": month_stats,
        "all_time": all_stats,
        "month_cache_rate": month_cache_rate,
        "today_cache_rate": today_cache_rate,
        "eom_rmb": eom_usd * USD_TO_RMB,
        "daily_avg_rmb": (month_stats["cost_usd"] * USD_TO_RMB / days_elapsed) if days_elapsed > 0 else 0,
        "recent_5": recent_5,
        "suggestions": suggestions,
        "days_in_month": days_in_month,
        "days_elapsed": days_elapsed,
    }


# ══════════════════════════════════════════════════════════
#  MERCURY ARCHIVE render  (default)
# ══════════════════════════════════════════════════════════

def render_hud_mercury(data, elapsed_sec=0):
    """Mercury Archive: archival ledger style token report."""
    L = []

    month_rmb = data["month"]["cost_usd"] * USD_TO_RMB
    today_rmb = data["today"]["cost_usd"] * USD_TO_RMB
    session_total = data["current"]["total"]
    month_str = data["now"].strftime("%Y-%m")
    eom_rmb = data["eom_rmb"]
    cache_rate = data["month_cache_rate"]
    model = data["model"]
    elapsed = f"{int(elapsed_sec // 60)}m {int(elapsed_sec % 60)}s"

    sp = sep_line

    # ── Header ──
    L.append('')
    L.append(f'  {c(t("bold"))}{c(t("accent"))}{t("title")}{c(RESET)}')
    L.append(f'  {c(t("dim"))}{t("subtitle")} // {month_str}{c(RESET)}')
    L.append(f'  {c(t("muted"))}MODEL{c(RESET)}  {c(t("dim"))}' + chr(0xB7) + f'{c(RESET)}  {model}')
    L.append(sp())

    # ── BUDGET ──
    L.append(f'  {section_label("BUDGET")}')

    d_ratio = today_rmb / DAILY_BUDGET if DAILY_BUDGET > 0 else 0
    d_bar = thin_bar(today_rmb, DAILY_BUDGET)
    d_pct = pct_str(today_rmb, DAILY_BUDGET)
    d_mark = threshold_marker(d_ratio)
    L.append(f'  {pad_col("Daily", 10)}{d_bar}  {d_pct}  {c(t("muted"))}RMB {today_rmb:.2f} / {DAILY_BUDGET:.2f}{c(RESET)}  {d_mark}')

    m_ratio = month_rmb / MONTHLY_BUDGET if MONTHLY_BUDGET > 0 else 0
    m_bar = thin_bar(month_rmb, MONTHLY_BUDGET)
    m_pct = pct_str(month_rmb, MONTHLY_BUDGET)
    m_mark = threshold_marker(m_ratio)
    L.append(f'  {pad_col("Monthly", 10)}{m_bar}  {m_pct}  {c(t("muted"))}RMB {month_rmb:.2f} / {MONTHLY_BUDGET:.2f}{c(RESET)}  EOM {c(t("muted"))}RMB {eom_rmb:.2f}{c(RESET)}  {m_mark}')

    s_ratio = session_total / SESSION_LARGE_THRESHOLD if SESSION_LARGE_THRESHOLD > 0 else 0
    s_bar = thin_bar(session_total, SESSION_LARGE_THRESHOLD)
    s_pct = pct_str(session_total, SESSION_LARGE_THRESHOLD)
    s_mark = threshold_marker(s_ratio)
    L.append(f'  {pad_col("Session", 10)}{s_bar}  {s_pct}  {c(t("muted"))}{format_tokens(session_total)} / 10M threshold{c(RESET)}  {s_mark}')

    # ── CACHE ──
    L.append(f'  {section_label("CACHE")}')
    c_bar = thin_bar(cache_rate, 100)
    c_pct = pct_str(cache_rate, 100)
    c_label = cache_status_label(cache_rate)
    L.append(f'  {pad_col("Hit Rate", 10)}{c_bar}  {c_pct}  {c(t("muted"))}{cache_rate:.1f}%{c(RESET)}  {c_label}')

    # ── TOTALS ──
    L.append(f'  {section_label("TOTALS")}')
    all_rmb = data["all_time"]["cost_usd"] * USD_TO_RMB
    L.append(f'  {pad_col("Today", 10)}    {c(t("muted"))}{data["today"]["count"]:>4} sessions{c(RESET)}    {format_tokens(data["today"]["total"]):>8} tokens    {c(ACCENT)}RMB {today_rmb:.2f}{c(RESET)}')
    L.append(f'  {pad_col("Month", 10)}    {c(t("muted"))}{data["month"]["count"]:>4} sessions{c(RESET)}    {format_tokens(data["month"]["total"]):>8} tokens    {c(ACCENT)}RMB {month_rmb:.2f}{c(RESET)}')
    L.append(f'  {pad_col("All Time", 10)}    {c(t("muted"))}{data["all_time"]["count"]:>4} sessions{c(RESET)}    {format_tokens(data["all_time"]["total"]):>8} tokens    {c(ACCENT)}RMB {all_rmb:.2f}{c(RESET)}')

    # ── RECENT SESSIONS (text-only, no bars) ──
    L.append(f'  {section_label("RECENT SESSIONS")}')
    for s in data["recent_5"]:
        dt = datetime.fromtimestamp(s["time_created"] / 1000, tz=CST)
        date_str = dt.strftime("%m-%d %H:%M")
        total = (s["tokens_input"] or 0) + (s["tokens_output"] or 0) + (s["tokens_reasoning"] or 0)
        cr = s["tokens_cache_read"] or 0
        input_like = (s["tokens_input"] or 0) + cr + (s["tokens_cache_write"] or 0)
        s_cache_rate = (cr / input_like * 100) if input_like > 0 else 0
        title = s["title"] or "(untitled)"
        if len(title) > 28:
            title = title[:25] + "..."
        L.append(f'  {c(t("muted"))}{date_str}{c(RESET)}  {format_tokens(total):>6} tokens  {c(t("muted"))}cache {s_cache_rate:.0f}%{c(RESET)}  {title}')

    # ── SUMMARY ──
    L.append(f'  {section_label("SUMMARY")}')
    lines_cn = _build_cn_summary(data, cache_rate)
    for line in lines_cn:
        L.append(f'  {c(t("dim"))}{line}{c(RESET)}')

    # ── Footer ──
    L.append(sp())
    L.append(f'  {c(t("dim"))}{t("footer")} {chr(0xA9)} 2026  {chr(0xB7)}  {model}  {chr(0xB7)}  {elapsed}{c(RESET)}')
    L.append('')

    return '\n'.join(L)


def _build_cn_summary(data, cache_rate):
    """Build natural Chinese summary lines."""
    lines = []
    month_rmb = data["month"]["cost_usd"] * USD_TO_RMB
    today_rmb = data["today"]["cost_usd"] * USD_TO_RMB
    eom_rmb = data["eom_rmb"]
    today_total = data["today"]["total"]
    month_count = data["month"]["count"]

    # budget status
    d_ratio = today_rmb / DAILY_BUDGET if DAILY_BUDGET > 0 else 0
    m_ratio = month_rmb / MONTHLY_BUDGET if MONTHLY_BUDGET > 0 else 0

    if d_ratio > 0.8:
        lines.append(f'日预算使用已超 80%（RMB {today_rmb:.2f} / {DAILY_BUDGET:.2f}），请注意当日用量。')
    elif today_rmb > 0:
        lines.append(f'日预算使用正常（RMB {today_rmb:.2f} / {DAILY_BUDGET:.2f}），月度预测稳定。')
    else:
        lines.append('今日暂无用量记录。')

    if m_ratio > 0.8:
        lines.append(f'月预算使用已超 80%（RMB {month_rmb:.2f} / {MONTHLY_BUDGET:.2f}），EOM 预测 RMB {eom_rmb:.2f}。')
    elif month_rmb > 0:
        lines.append(f'月末预测 RMB {eom_rmb:.2f}，在预算范围内。')

    # cache
    if cache_rate >= 90:
        lines.append(f'Cache 命中率 {cache_rate:.1f}%，上下文复用表现优秀。')
    elif cache_rate >= 70:
        lines.append(f'Cache 命中率 {cache_rate:.1f}%，处于正常区间。')
    else:
        lines.append(f'Cache 命中率 {cache_rate:.1f}%，偏低，可能频繁新建会话或上下文变化较大。')

    # session anomalies
    anomalies = detect_anomalies(data["recent_5"])
    large_count = sum(1 for _, tags in anomalies if 'large' in tags)
    lowc_count = sum(1 for _, tags in anomalies if 'low_cache' in tags)
    if large_count > 0:
        lines.append(f'注意到 {large_count} 个会话超过 10M tokens，建议检查任务拆分方式。')
    if lowc_count > 0:
        lines.append(f'注意到 {lowc_count} 个会话 Cache 率低于 30%，新会话开销较大。')
    if today_total > 100_000_000:
        lines.append(f'今日用量较高（{format_tokens(today_total)}），请确认无异常会话。')
    if month_count > 100:
        lines.append(f'本月已开启 {month_count} 个会话，频繁新建会话会降低 Cache 利用率。')

    return lines


# ══════════════════════════════════════════════════════════
#  Compact render (--compact)  — Mercury style
# ══════════════════════════════════════════════════════════

def render_compact_mercury(data, elapsed_sec=0):
    L = []
    month_rmb = data["month"]["cost_usd"] * USD_TO_RMB
    today_rmb = data["today"]["cost_usd"] * USD_TO_RMB
    cache_rate = data["month_cache_rate"]
    month_str = data["now"].strftime("%Y-%m")
    model = data["model"]
    elapsed = f"{int(elapsed_sec // 60)}m {int(elapsed_sec % 60)}s"

    L.append('')
    L.append(f'  {c(t("bold"))}{c(t("accent"))}{t("title")}{c(RESET)}  {c(t("muted"))}{month_str} ' + chr(0xB7) + f' {model}{c(RESET)}')
    L.append(f'  {c(t("dim"))}{t("line") * (t("width") - 6)}{c(RESET)}')

    d_ratio = today_rmb / DAILY_BUDGET if DAILY_BUDGET > 0 else 0
    m_ratio = month_rmb / MONTHLY_BUDGET if MONTHLY_BUDGET > 0 else 0
    L.append(f'  {section_label("BUDGET")}  Daily {pct_str(today_rmb, DAILY_BUDGET)}  {c(t("muted"))}RMB {today_rmb:.2f} / {DAILY_BUDGET:.2f}{c(RESET)}  {threshold_marker(d_ratio)}')
    L.append(f'            Monthly {pct_str(month_rmb, MONTHLY_BUDGET)}  {c(t("muted"))}RMB {month_rmb:.2f} / {MONTHLY_BUDGET:.2f}{c(RESET)}  EOM RMB {data["eom_rmb"]:.2f}  {threshold_marker(m_ratio)}')
    L.append(f'            Cache {c(t("muted"))}{cache_rate:.1f}%{c(RESET)}  {cache_status_label(cache_rate)}')

    all_rmb = data["all_time"]["cost_usd"] * USD_TO_RMB
    L.append(f'  {section_label("TOTALS")}  Today {c(t("muted"))}{data["today"]["count"]} sess  {format_tokens(data["today"]["total"])}  RMB {today_rmb:.2f}{c(RESET)}')
    L.append(f'            Month {c(t("muted"))}{data["month"]["count"]} sess  {format_tokens(data["month"]["total"])}  RMB {month_rmb:.2f}{c(RESET)}')
    L.append(f'            All Time {c(t("muted"))}{data["all_time"]["count"]} sess  {format_tokens(data["all_time"]["total"])}  RMB {all_rmb:.2f}{c(RESET)}')

    L.append(f'  {c(t("dim"))}{t("line") * (t("width") - 6)}{c(RESET)}')
    for s in data["recent_5"]:
        dt = datetime.fromtimestamp(s["time_created"] / 1000, tz=CST)
        date_str = dt.strftime("%m-%d %H:%M")
        total = (s["tokens_input"] or 0) + (s["tokens_output"] or 0) + (s["tokens_reasoning"] or 0)
        cr = s["tokens_cache_read"] or 0
        input_like = (s["tokens_input"] or 0) + cr + (s["tokens_cache_write"] or 0)
        s_cache_rate = (cr / input_like * 100) if input_like > 0 else 0
        title = s["title"] or "(untitled)"
        if len(title) > 28:
            title = title[:25] + "..."
        L.append(f'  {c(t("muted"))}{date_str}{c(RESET)}  {format_tokens(total):>6} tokens  {c(t("muted"))}cache {s_cache_rate:.0f}%{c(RESET)}  {title}')

    L.append(f'  {c(t("dim"))}{t("line") * (t("width") - 6)}{c(RESET)}')
    L.append(f'  {c(t("dim"))}{t("footer")} {chr(0xA9)} 2026  {chr(0xB7)}  {model}  {chr(0xB7)}  {elapsed}{c(RESET)}')
    L.append('')
    return '\n'.join(L)


# ══════════════════════════════════════════════════════════
#  Detail render (--detail)
# ══════════════════════════════════════════════════════════

def render_detail(data):
    """Render detailed view with per-session breakdown."""
    lines = []
    W = 56

    now = data["now"]
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = int(today_start.timestamp() * 1000)

    # Get today's sessions with detail
    conn = sqlite3.connect(str(DB_PATH))
    today_sessions = get_sessions(conn, "WHERE time_created >= ?", (today_ts,))
    conn.close()

    lines.append(f"Token Detail  {now.strftime('%Y-%m-%d')}")
    lines.append("=" * W)

    if not today_sessions:
        lines.append("  No sessions today.")
        return "\n".join(lines)

    for s in today_sessions:
        dt = datetime.fromtimestamp(s["time_created"] / 1000, tz=CST)
        date_str = dt.strftime("%m-%d %H:%M")
        total = (s["tokens_input"] or 0) + (s["tokens_output"] or 0) + (s["tokens_reasoning"] or 0)
        cache = s["tokens_cache_read"] or 0
        input_like = (s["tokens_input"] or 0) + cache + (s["tokens_cache_write"] or 0)
        s_cache_rate = (cache / input_like * 100) if input_like > 0 else 0
        rmb = (s["cost"] or 0) * USD_TO_RMB
        title = s["title"] or "(untitled)"
        if len(title) > 30:
            title = title[:27] + "..."

        lines.append(f"  {date_str}  {title}")
        lines.append(f"           in:{format_tokens(s['tokens_input'] or 0):>6}  out:{format_tokens(s['tokens_output'] or 0):>6}  reasoning:{format_tokens(s['tokens_reasoning'] or 0):>6}")
        lines.append(f"           cache:{format_tokens(cache)}  rate:{s_cache_rate:.0f}%  cost: RMB {rmb:.2f}")
        lines.append("")

    today_stats = aggregate(today_sessions)
    lines.append("=" * W)
    lines.append(f"  Today total: {today_stats['count']} sessions  in:{format_tokens(today_stats['input'])}  out:{format_tokens(today_stats['output'])}  RMB {today_stats['cost_usd'] * USD_TO_RMB:.2f}")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
#  JSON output (--json)
# ══════════════════════════════════════════════════════════

def output_json(data):
    """Output JSON for tool consumption."""
    now = data["now"]
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = int(today_start.timestamp() * 1000)

    conn = sqlite3.connect(str(DB_PATH))
    all_sessions = get_sessions(conn)
    conn.close()

    result = {
        "timestamp": now.isoformat(),
        "model": data["model"],
        "current_session": data["current"],
        "today": data["today"],
        "month": data["month"],
        "all_time": data["all_time"],
        "cache_hit_rate": data["month_cache_rate"],
        "eom_projection_rmb": data["eom_rmb"],
        "sessions": [],
    }

    for s in all_sessions:
        result["sessions"].append({
            "id": s["id"],
            "title": s["title"],
            "model": parse_model(s["model"]),
            "tokens_input": s["tokens_input"] or 0,
            "tokens_output": s["tokens_output"] or 0,
            "tokens_reasoning": s["tokens_reasoning"] or 0,
            "tokens_cache_read": s["tokens_cache_read"] or 0,
            "cost_usd": s["cost"] or 0,
            "cost_rmb": (s["cost"] or 0) * USD_TO_RMB,
            "time_created": s["time_created"],
        })

    print(json.dumps(result, indent=2, ensure_ascii=False))


# ══════════════════════════════════════════════════════════
#  Single-value modes (--session, --today, --month)
# ══════════════════════════════════════════════════════════

def run_session(conn):
    sessions = get_sessions(conn, limit=1)
    if not sessions:
        print(f'  {c(t("muted"))}No sessions found.{c(RESET)}')
        return
    s = sessions[0]
    total = (s["tokens_input"] or 0) + (s["tokens_output"] or 0) + (s["tokens_reasoning"] or 0)
    cache = s["tokens_cache_read"] or 0
    input_like = (s["tokens_input"] or 0) + cache + (s["tokens_cache_write"] or 0)
    rate = (cache / input_like * 100) if input_like > 0 else 0
    rmb = (s["cost"] or 0) * USD_TO_RMB
    print()
    print(f'  {c(t("bold"))}Current Session{c(RESET)}    {format_tokens(total)} tokens    {c(ACCENT)}RMB {rmb:.2f}{c(RESET)}    {c(t("muted"))}cache {rate:.0f}%{c(RESET)}')
    print()


def run_today(conn):
    now = datetime.now(CST)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = int(today_start.timestamp() * 1000)
    sessions = get_sessions(conn, "WHERE time_created >= ?", (today_ts,))
    stats = aggregate(sessions)
    rmb = stats["cost_usd"] * USD_TO_RMB
    rate = cache_hit_rate(stats["cache_read"], stats["input"], stats["cache_write"])
    bar = thin_bar(rmb, DAILY_BUDGET)
    pct = pct_str(rmb, DAILY_BUDGET)
    mark = threshold_marker(rmb / DAILY_BUDGET if DAILY_BUDGET > 0 else 0)
    print()
    print(f'  {section_label("TODAY")}  {now.strftime("%Y-%m-%d")}')
    print(f'  {c(t("muted"))}{stats["count"]} sessions{c(RESET)}    {format_tokens(stats["total"])} tokens    {c(t("muted"))}Cache {rate:.0f}%{c(RESET)}')
    print(f'  {pad_col("Budget", 10)}{bar}  {pct}  {c(t("muted"))}RMB {rmb:.2f} / {DAILY_BUDGET:.2f}{c(RESET)}  {mark}')
    print()


def run_month(conn):
    now = datetime.now(CST)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_ts = int(month_start.timestamp() * 1000)
    sessions = get_sessions(conn, "WHERE time_created >= ?", (month_ts,))
    stats = aggregate(sessions)
    rmb = stats["cost_usd"] * USD_TO_RMB
    rate = cache_hit_rate(stats["cache_read"], stats["input"], stats["cache_write"])
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_elapsed = now.day
    eom = compute_eom(stats["cost_usd"], days_elapsed, days_in_month) * USD_TO_RMB
    bar = thin_bar(rmb, MONTHLY_BUDGET)
    pct = pct_str(rmb, MONTHLY_BUDGET)
    mark = threshold_marker(rmb / MONTHLY_BUDGET if MONTHLY_BUDGET > 0 else 0)
    print()
    print(f'  {section_label("MONTH")}  {now.strftime("%Y-%m")}')
    print(f'  {c(t("muted"))}{stats["count"]} sessions{c(RESET)}    {format_tokens(stats["total"])} tokens    {c(t("muted"))}Cache {rate:.0f}%{c(RESET)}')
    print(f'  {pad_col("Budget", 10)}{bar}  {pct}  {c(t("muted"))}RMB {rmb:.2f} / {MONTHLY_BUDGET:.2f}  EOM RMB {eom:.2f}{c(RESET)}  {mark}')
    print()


# ══════════════════════════════════════════════════════════
#  Main entry
# ══════════════════════════════════════════════════════════

def main():
    t0 = datetime.now()
    args = sys.argv[1:]

    if "--no-color" in args:
        disable_colors()

    if not DB_PATH.exists():
        print(f"Error: OpenCode database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))

    try:
        if "--session" in args:
            run_session(conn)
        elif "--today" in args:
            run_today(conn)
        elif "--month" in args:
            run_month(conn)
        elif "--json" in args:
            data = build_dashboard_data(conn)
            if data is None:
                print("No sessions found.")
                return
            output_json(data)
        elif "--detail" in args:
            data = build_dashboard_data(conn)
            if data is None:
                print("No sessions found.")
                return
            print(render_detail(data))
        elif "--compact" in args:
            data = build_dashboard_data(conn)
            if data is None:
                print("No sessions found.")
                return
            elapsed = (datetime.now() - t0).total_seconds()
            print(render_compact_mercury(data, elapsed))
        else:
            data = build_dashboard_data(conn)
            if data is None:
                print("No sessions found.")
                return
            elapsed = (datetime.now() - t0).total_seconds()
            print(render_hud_mercury(data, elapsed))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
