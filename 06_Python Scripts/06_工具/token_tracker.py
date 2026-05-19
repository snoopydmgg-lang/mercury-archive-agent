#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Token 使用量追踪器 - 本地累积统计
用法:
  python token_tracker.py                    # 仪表盘（简洁模式）
  python token_tracker.py --detail           # 仪表盘（详细模式）
  python token_tracker.py --session          # 仅当前 session
  python token_tracker.py --today            # 仅今天
  python token_tracker.py --month            # 仅本月
  python token_tracker.py --json             # JSON 输出（供其他脚本消费）
  python token_tracker.py --update-cache     # 强制更新缓存
"""

import json
import sys
import io
import os
import calendar
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import defaultdict

# ── 费率配置 ──────────────────────────────────────────────
PRICING = {
    "deepseek-v4-pro": {
        "input": 0.14,
        "output": 0.28,
        "cache_hit": 0.014,
        "currency": "RMB",
        "note": "DeepSeek V4 Pro standard pricing, cache read = 2.5折 promo"
    },
}

DEFAULT_MODEL = "deepseek-v4-pro"

# Anthropic 模型名 → 计费模型名（transcript 中记录的模型名映射到实际计费）
MODEL_ALIAS_MAP = {
    "claude-opus-4-7": "deepseek-v4-pro",
    "deepseek-v4-pro": "deepseek-v4-pro",
}

CACHE_VERSION = 2

# Windows 终端编码
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOME = Path.home()
PROJECTS_DIR = HOME / '.claude' / 'projects'
CACHE_FILE = HOME / '.claude' / '.token_usage_cache.json'
CACHE_TTL_HOURS = 1

ANSI_RED = '\033[91m'
ANSI_YELLOW = '\033[93m'
ANSI_GREEN = '\033[92m'
ANSI_CYAN = '\033[96m'
ANSI_RESET = '\033[0m'
ANSI_BOLD = '\033[1m'
ANSI_DIM = '\033[2m'

# ── SQLite 持久化配置 ────────────────────────────────────
DB_PATH = str(Path(__file__).resolve().parent.parent / 'token_metrics.db')
DAILY_BUDGET = 10.00
MONTHLY_BUDGET = 200.00


def format_tokens(n):
    if n >= 1_000_000:
        return f'{n/1_000_000:.2f}M'
    elif n >= 1_000:
        return f'{n/1_000:.1f}K'
    return str(n)


def resolve_model(transcript_model):
    """将 transcript 中记录的模型名映射到计费模型名"""
    if not transcript_model:
        return DEFAULT_MODEL
    return MODEL_ALIAS_MAP.get(transcript_model, DEFAULT_MODEL)


def calculate_cost(input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens, model=None):
    """分别计算 Input / Output / Cache 的真实成本并加总"""
    model = resolve_model(model)
    pricing = PRICING.get(model, PRICING[DEFAULT_MODEL])

    # cache_creation 按 input 费率计费，cache_read 按折扣费率
    billable_input = input_tokens + cache_creation_tokens
    input_cost = billable_input / 1_000_000 * pricing['input']
    output_cost = output_tokens / 1_000_000 * pricing['output']
    cache_cost = cache_read_tokens / 1_000_000 * pricing['cache_hit']

    return {
        'input_cost': input_cost,
        'output_cost': output_cost,
        'cache_cost': cache_cost,
        'total': input_cost + output_cost + cache_cost,
        'model': model,
        'pricing': pricing,
        'currency': pricing.get('currency', 'USD'),
    }


# ══════════════════════════════════════════════════════════
#  SQLite 持久化引擎
# ══════════════════════════════════════════════════════════

def init_db():
    """初始化 SQLite 数据库与表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            session_id TEXT UNIQUE,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cache_read_tokens INTEGER DEFAULT 0,
            cache_creation_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            input_cost REAL DEFAULT 0.0,
            output_cost REAL DEFAULT 0.0,
            cache_cost REAL DEFAULT 0.0,
            total_cost REAL DEFAULT 0.0,
            model TEXT,
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(date)
    ''')
    conn.commit()
    conn.close()


def run_alerts():
    """执行 SQL 聚合查询并触发熔断逻辑

    日度阈值: DAILY_BUDGET (¥10.00) — 超限黄色警告
    月度熔断: MONTHLY_BUDGET (¥200.00) — EOM Run-Rate 超限则 exit(1)
    绕过熔断: 传 --confirm-overbudget 参数
    """
    init_db()  # 幂等建表，确保 schema 存在
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = date.today().isoformat()
    current_month = date.today().strftime('%Y-%m')

    # O(1) 聚合查询：今日总成本
    cursor.execute("SELECT SUM(total_cost) FROM metrics WHERE date = ?", (today,))
    daily_cost = cursor.fetchone()[0] or 0.0

    # O(1) 聚合查询：本月总成本
    cursor.execute("SELECT SUM(total_cost) FROM metrics WHERE date LIKE ?", (f"{current_month}%",))
    monthly_cost = cursor.fetchone()[0] or 0.0

    conn.close()

    # 计算月末预测账单 (Run-Rate)
    now = datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    current_day = now.day
    run_rate = (monthly_cost / current_day) * days_in_month if current_day > 0 else 0.0

    print(f"\n{ANSI_BOLD}[Token Metrics]{ANSI_RESET} Daily: ¥{daily_cost:.4f} | Monthly: ¥{monthly_cost:.4f} | EOM Run-Rate: ¥{run_rate:.4f}")

    # 日度告警（仅黄色高亮警告）
    if daily_cost > DAILY_BUDGET:
        print(f"{ANSI_YELLOW}[WARNING] Daily budget exceeded! (¥{daily_cost:.2f} / ¥{DAILY_BUDGET:.2f}){ANSI_RESET}")

    # 月度熔断（强制阻断）
    if run_rate > MONTHLY_BUDGET:
        print(f"\n{ANSI_RED}{ANSI_BOLD}[CIRCUIT BREAKER]{ANSI_RESET} {ANSI_RED}EOM Run-Rate (¥{run_rate:.2f}) exceeds monthly budget (¥{MONTHLY_BUDGET:.2f})!{ANSI_RESET}")
        print(f"{ANSI_RED}Execution halted to prevent budget overrun.{ANSI_RESET}")

        if "--confirm-overbudget" not in sys.argv:
            sys.exit(1)
        else:
            print(f"{ANSI_YELLOW}Bypass flag '--confirm-overbudget' detected. Continuing execution...{ANSI_RESET}")


def save_session_to_db(session_data):
    """将单次会话的 Token 消耗写入 SQLite（幂等：session_id UNIQUE 约束防重复）"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO metrics (
                date, session_id, input_tokens, output_tokens,
                cache_read_tokens, cache_creation_tokens, total_tokens,
                input_cost, output_cost, cache_cost, total_cost, model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date.today().isoformat(),
            session_data.get('session_id', 'unknown'),
            session_data.get('input_tokens', 0),
            session_data.get('output_tokens', 0),
            session_data.get('cache_read_tokens', 0),
            session_data.get('cache_creation_tokens', 0),
            session_data.get('total_tokens', 0),
            session_data.get('input_cost', 0.0),
            session_data.get('output_cost', 0.0),
            session_data.get('cache_cost', 0.0),
            session_data.get('total_cost', 0.0),
            session_data.get('model', DEFAULT_MODEL)
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def sync_cache_to_db(cache):
    """将 JSON 缓存中的所有 session 同步到 SQLite（全量幂等写入）"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    written = 0
    for s in cache.get('sessions', []):
        cost = calculate_cost(
            s['input'], s['output'],
            s.get('cache_read', 0), s.get('cache_creation', 0),
            s.get('model')
        )
        session_id = Path(s.get('file', 'unknown')).stem
        try:
            cursor.execute('''
                INSERT INTO metrics (
                    date, session_id, input_tokens, output_tokens,
                    cache_read_tokens, cache_creation_tokens, total_tokens,
                    input_cost, output_cost, cache_cost, total_cost, model
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                s['date'], session_id,
                s['input'], s['output'],
                s.get('cache_read', 0), s.get('cache_creation', 0),
                s['total'],
                cost['input_cost'], cost['output_cost'], cost['cache_cost'],
                cost['total'], cost['model']
            ))
            written += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return written


def get_transcript_dirs():
    if not PROJECTS_DIR.exists():
        return []
    dirs = []
    for d in PROJECTS_DIR.iterdir():
        if d.is_dir():
            jsonl_files = list(d.glob('*.jsonl'))
            if jsonl_files:
                dirs.append(d)
    return dirs


def parse_transcript(filepath):
    """解析单个 transcript 文件

    Returns:
        (session_date, session_time, input_tokens, output_tokens,
         cache_read_tokens, cache_creation_tokens, model)
    """
    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_creation = 0
    session_date = None
    session_time = None
    model = None

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if session_date is None and 'timestamp' in msg:
                    ts = msg['timestamp']
                    try:
                        session_date = ts[:10]
                        session_time = ts[11:16] if len(ts) >= 16 else None
                    except Exception:
                        pass

                usage = msg.get('message', {}).get('usage')
                if not usage:
                    continue

                total_input += usage.get('input_tokens', 0)
                total_output += usage.get('output_tokens', 0)
                total_cache_read += usage.get('cache_read_input_tokens', 0)
                total_cache_creation += usage.get('cache_creation_input_tokens', 0)

                if model is None:
                    model = msg.get('message', {}).get('model')
    except Exception:
        pass

    if session_date is None:
        mtime = os.path.getmtime(filepath)
        dt = datetime.fromtimestamp(mtime)
        session_date = dt.strftime('%Y-%m-%d')
        session_time = dt.strftime('%H:%M')

    return session_date, session_time, total_input, total_output, total_cache_read, total_cache_creation, model


def collect_all_usage(force=False):
    if not force and CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding='utf-8'))
            if cache.get('version') == CACHE_VERSION:
                cache_time = datetime.fromisoformat(cache['updated_at'])
                if datetime.now() - cache_time < timedelta(hours=CACHE_TTL_HOURS):
                    return cache
        except Exception:
            pass

    sessions = []
    daily = defaultdict(lambda: {
        'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0, 'sessions': 0
    })
    monthly = defaultdict(lambda: {
        'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0, 'sessions': 0
    })

    for proj_dir in get_transcript_dirs():
        for jsonl_file in proj_dir.glob('*.jsonl'):
            size = jsonl_file.stat().st_size
            if size == 0 or size > 100_000_000:
                continue

            result = parse_transcript(jsonl_file)
            s_date, s_time, s_input, s_output, s_cache_read, s_cache_creation, s_model = result

            if s_input + s_output + s_cache_read + s_cache_creation == 0:
                continue

            sessions.append({
                'date': s_date,
                'time': s_time or '',
                'file': str(jsonl_file),
                'input': s_input,
                'output': s_output,
                'cache_read': s_cache_read,
                'cache_creation': s_cache_creation,
                'cache_total': s_cache_read + s_cache_creation,
                'total': s_input + s_output + s_cache_read + s_cache_creation,
                'model': s_model,
            })

            daily[s_date]['input'] += s_input
            daily[s_date]['output'] += s_output
            daily[s_date]['cache_read'] += s_cache_read
            daily[s_date]['cache_creation'] += s_cache_creation
            daily[s_date]['sessions'] += 1

            month_key = s_date[:7]
            monthly[month_key]['input'] += s_input
            monthly[month_key]['output'] += s_output
            monthly[month_key]['cache_read'] += s_cache_read
            monthly[month_key]['cache_creation'] += s_cache_creation
            monthly[month_key]['sessions'] += 1

    sessions.sort(key=lambda s: s['date'] + s.get('time', ''), reverse=True)

    cache_data = {
        'version': CACHE_VERSION,
        'updated_at': datetime.now().isoformat(),
        'sessions': sessions,
        'daily': {k: dict(v) for k, v in sorted(daily.items(), reverse=True)},
        'monthly': {k: dict(v) for k, v in sorted(monthly.items(), reverse=True)},
    }

    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass

    # 同步到 SQLite（幂等写入，不阻塞主流程）
    try:
        sync_cache_to_db(cache_data)
    except Exception:
        pass

    return cache_data


def get_current_session_id():
    current_proj = Path.cwd()
    proj_key = str(current_proj).replace(':', '-').replace('\\', '-').replace('.', '-')
    proj_dir = PROJECTS_DIR / proj_key
    if not proj_dir.exists():
        return None
    jsonl_files = list(proj_dir.glob('*.jsonl'))
    if not jsonl_files:
        return None
    return max(jsonl_files, key=lambda f: f.stat().st_mtime)


def get_session_bar(value, max_value, width=20):
    """绘制单 session 柱状条"""
    filled = int(value / max_value * width) if max_value > 0 else 1
    return f'{"█" * filled}{"░" * (width - filled)}'


def get_cache_status(rate):
    """Return (icon_label, color) for cache hit rate status."""
    if rate >= 90:
        return '\U0001f7e2 优秀', ANSI_GREEN
    elif rate >= 70:
        return '\U0001f7e1 正常', ANSI_YELLOW
    else:
        return '\U0001f534 偏低', ANSI_RED


def detect_anomalies(sessions, large_threshold=10_000_000):
    """Detect sessions with >10M tokens or cache hit rate < 30%."""
    results = []
    for s in sessions:
        tags = []
        if s['total'] > large_threshold:
            tags.append('large')
        input_like = s['input'] + s.get('cache_creation', 0) + s.get('cache_read', 0)
        s_cache_rate = (s.get('cache_read', 0) / input_like * 100 if input_like > 0 else 0)
        if s_cache_rate < 30 and input_like > 1_000_000:
            tags.append('low_cache')
        if tags:
            results.append((s, tags))
    return results


def generate_suggestions(cache_hit_rate, today_tokens, recent_sessions, month_sessions):
    """Generate cost optimization suggestions. Returns list of (level, text)."""
    suggestions = []

    if cache_hit_rate >= 90:
        suggestions.append(('good', '上下文复用良好，Cache 命中率优秀'))
    elif cache_hit_rate < 70:
        suggestions.append(('warn', 'Cache 命中率偏低 —— 可能频繁新开会话或上下文变化过大'))

    anomalies = detect_anomalies(recent_sessions[:10])
    large_count = sum(1 for _, tags in anomalies if 'large' in tags)
    lowc_count = sum(1 for _, tags in anomalies if 'low_cache' in tags)

    if large_count > 0:
        suggestions.append(('warn', f'最近 {large_count} 个 Session 超过 10M tokens,建议检查任务拆分'))
    if lowc_count > 0:
        suggestions.append(('warn', f'最近 {lowc_count} 个 Session Cache 命中率 <30%,新会话开销较大'))

    if today_tokens > 100_000_000:
        suggestions.append(('warn', '今日用量较高 (>100M),建议检查是否有异常大 Session'))

    if month_sessions > 100:
        suggestions.append(('info', f'本月已开 {month_sessions} 个 Session,频繁新开会话会降低 Cache 利用率'))

    if not suggestions:
        suggestions.append(('good', '各项指标正常'))

    return suggestions


def display_full(cache, detail=False):
    today_str = date.today().isoformat()
    this_month = today_str[:7]
    today = date.today()

    # ── 聚合本月数据 ──
    month_total_in = 0
    month_total_out = 0
    month_total_cr = 0
    month_total_cc = 0
    month_sessions = 0
    for m_key, m_data in cache['monthly'].items():
        if m_key == this_month:
            month_total_in += m_data['input']
            month_total_out += m_data['output']
            month_total_cr += m_data.get('cache_read', 0)
            month_total_cc += m_data.get('cache_creation', 0)
            month_sessions += m_data['sessions']

    month_total_tokens = month_total_in + month_total_out + month_total_cr + month_total_cc

    # 缓存命中率
    month_input_like = month_total_in + month_total_cc + month_total_cr
    cache_hit_rate = (month_total_cr / month_input_like * 100
                      if month_input_like > 0 else 0)

    # 费用计算
    cost = calculate_cost(month_total_in, month_total_out, month_total_cr, month_total_cc)
    month_cost = cost['total']

    # 月末预测
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    eom_prediction = (month_cost / days_elapsed * days_in_month
                      if days_elapsed > 0 else 0)
    daily_avg_cost = month_cost / days_elapsed if days_elapsed > 0 else 0

    # ── 本次 Session ──
    current_file = get_current_session_id()
    s_in = s_out = s_cr = s_cc = 0
    if current_file:
        _, _, s_in, s_out, s_cr, s_cc, _ = parse_transcript(current_file)
    s_total = s_in + s_out + s_cr + s_cc

    # ── 今日 ──
    today_data = cache['daily'].get(today_str, {
        'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0, 'sessions': 0
    })
    t_in = today_data['input']
    t_out = today_data['output']
    t_cr = today_data.get('cache_read', 0)
    t_cc = today_data.get('cache_creation', 0)
    t_total = t_in + t_out + t_cr + t_cc
    t_sessions = today_data['sessions']

    # ── 历史总计 ──
    all_in = sum(s_['input'] for s_ in cache['sessions'])
    all_out = sum(s_['output'] for s_ in cache['sessions'])
    all_cr = sum(s_.get('cache_read', 0) for s_ in cache['sessions'])
    all_cc = sum(s_.get('cache_creation', 0) for s_ in cache['sessions'])
    all_total = all_in + all_out + all_cr + all_cc
    all_sessions = len(cache['sessions'])

    # ── 状态 / 异常 / 建议 ──
    cache_status, cache_color = get_cache_status(cache_hit_rate)
    recent_5 = cache['sessions'][:5]
    suggestions = generate_suggestions(cache_hit_rate, t_total, recent_5, month_sessions)

    # ── 色彩 ──
    C, R, B, D, G, Y = ANSI_CYAN, ANSI_RESET, ANSI_BOLD, ANSI_DIM, ANSI_GREEN, ANSI_YELLOW
    M = '\033[95m'
    eom_color = ANSI_RED if eom_prediction > MONTHLY_BUDGET else ''
    eom_reset = ANSI_RESET if eom_prediction > MONTHLY_BUDGET else ''

    W = 66  # 面板总宽度

    def strip_ansi(text):
        """Remove ANSI escape codes from text to measure visible length."""
        result = ''
        i = 0
        while i < len(text):
            if text[i] == '\033' and i + 1 < len(text) and text[i + 1] == '[':
                i += 2
                while i < len(text) and text[i] not in 'mHJABCDEFGKSThlfsu':
                    i += 1
                i += 1  # skip the terminating char
            else:
                result += text[i]
                i += 1
        return result

    def panel_line(content=''):
        """Print a line within the panel with right-aligned border."""
        visible_len = len(strip_ansi(content))
        pad = max(0, W - 4 - visible_len)
        print(f"{C}│{R} {content}{' ' * pad} {C}│{R}")

    def panel_sep():
        print(f"{C}├{'─' * (W - 2)}┤{R}")

    # ═══════════════════════════════════════════
    #  Header
    # ═══════════════════════════════════════════
    print(f"\n{C}╭{'─' * (W - 2)}╮{R}")
    panel_line(f"{B}Token 仪表盘 · {this_month}{R}    {D}{cost['model']}{R}")
    panel_sep()

    # ── 1. 费用概览 ──
    panel_line(f"{B}费用概览{R}")
    panel_line(f"  本月累计 {B}¥{month_cost:.2f}{R}  |  日均 ¥{daily_avg_cost:.2f}  |  月末预测 {eom_color}¥{eom_prediction:.2f}{eom_reset}")
    if detail:
        panel_line(f"  {D}({days_elapsed}/{days_in_month} 天, 本月 {month_sessions} 个 Session){R}")
    panel_line()

    # ── 2. Token 概览 ──
    panel_line(f"{B}Token 概览{R}")
    panel_line(f"  本次 {format_tokens(s_total):>8}  |  今日 {format_tokens(t_total):>8}  |  本月 {format_tokens(month_total_tokens):>8}")
    if detail:
        panel_line(f"  输入 {format_tokens(month_total_in):>8}  |  输出 {format_tokens(month_total_out):>8}  |  Cache {format_tokens(month_total_cr + month_total_cc):>8}")
        panel_line(f"  历史 {format_tokens(all_total):>8}  |  {all_sessions} Sessions")
    panel_line()

    # ── 3. Cache 状态 ──
    panel_line(f"{B}Cache 状态{R}      {cache_color}{cache_status}  {cache_hit_rate:.1f}%{R}")
    if detail:
        panel_line(f"  Cache Read  {format_tokens(month_total_cr):>8}    命中率基数  {format_tokens(month_input_like):>8}")
    panel_line()

    # ── 4. 费用拆分 ──
    panel_line(f"{B}费用拆分{R}  {D}(@¥/M: I={cost['pricing']['input']} O={cost['pricing']['output']} C={cost['pricing']['cache_hit']}){R}")
    panel_line(f"  Input {B}¥{cost['input_cost']:.2f}{R}  |  Output {B}¥{cost['output_cost']:.2f}{R}  |  Cache {B}¥{cost['cache_cost']:.2f}{R}")
    if detail:
        panel_line(f"  {D}Input:  {format_tokens(month_total_in + month_total_cc):>8} x ¥{cost['pricing']['input']}/M   = ¥{cost['input_cost']:.2f}{R}")
        panel_line(f"  {D}Output: {format_tokens(month_total_out):>8} x ¥{cost['pricing']['output']}/M  = ¥{cost['output_cost']:.2f}{R}")
        panel_line(f"  {D}Cache:  {format_tokens(month_total_cr):>8} x ¥{cost['pricing']['cache_hit']}/M = ¥{cost['cache_cost']:.2f}{R}")
    panel_line()

    # ── 5. 最近 5 个 Session ──
    panel_line(f"{B}最近 5 个 Session{R}")
    max_total = max(s_['total'] for s_ in recent_5) if recent_5 else 1

    for s_ in recent_5:
        total = s_['total']
        input_like = s_['input'] + s_.get('cache_creation', 0) + s_.get('cache_read', 0)
        s_cache_rate = (s_.get('cache_read', 0) / input_like * 100 if input_like > 0 else 0)
        bar = get_session_bar(total, max_total)
        time_part = f" {s_.get('time', '')}" if s_.get('time') else ''
        date_part = s_['date'][5:]  # MM-DD

        is_large = total > 10_000_000
        is_low_cache = s_cache_rate < 30 and input_like > 1_000_000

        flags = ''
        if is_large:
            flags += f' {ANSI_RED}!!{ANSI_RESET}'
        if is_low_cache:
            flags += f' {ANSI_YELLOW}c{ANSI_RESET}'

        if is_large:
            entry = f"  {ANSI_RED}{date_part}{time_part}  {format_tokens(total):>8}  {bar}  c{s_cache_rate:.0f}%{flags}{ANSI_RESET}"
        else:
            entry = f"  {date_part}{time_part}  {format_tokens(total):>8}  {bar}  c{s_cache_rate:.0f}%{flags}"
        panel_line(entry)

        if detail:
            panel_line(f"  {D}In:{format_tokens(s_['input']):>7} Out:{format_tokens(s_['output']):>7} CR:{format_tokens(s_.get('cache_read', 0)):>7} CC:{format_tokens(s_.get('cache_creation', 0)):>7}{R}")
    panel_line()

    # ── 6. 今日建议 ──
    panel_line(f"{B}今日建议{R}")
    for level, text in suggestions:
        if level == 'good':
            icon = f'{ANSI_GREEN}OK{ANSI_RESET}'
        elif level == 'warn':
            icon = f'{ANSI_YELLOW}!!{ANSI_RESET}'
        else:
            icon = f'{C}--{R}'
        panel_line(f"  [{icon}] {text}")
    panel_line()

    # ── Footer ──
    print(f"{C}╰{'─' * (W - 2)}╯{R}\n")


def output_json(cache):
    today_str = date.today().isoformat()
    this_month = today_str[:7]
    today = date.today()

    current_file = get_current_session_id()
    session_data = None
    if current_file:
        result = parse_transcript(current_file)
        s_date, s_time, s_in, s_out, s_cr, s_cc, s_model = result
        s_cost = calculate_cost(s_in, s_out, s_cr, s_cc, s_model)
        session_data = {
            'input': s_in, 'output': s_out,
            'cache_read': s_cr, 'cache_creation': s_cc,
            'total': s_in + s_out + s_cr + s_cc,
            'model': s_model,
            'cost': s_cost,
        }

    today_data = cache['daily'].get(today_str, {})
    today_tokens = (today_data.get('input', 0) + today_data.get('output', 0)
                    + today_data.get('cache_read', 0) + today_data.get('cache_creation', 0))

    month_total_in = 0
    month_total_out = 0
    month_total_cr = 0
    month_total_cc = 0
    month_sessions = 0
    for m_key, m_data in cache['monthly'].items():
        if m_key == this_month:
            month_total_in += m_data['input']
            month_total_out += m_data['output']
            month_total_cr += m_data.get('cache_read', 0)
            month_total_cc += m_data.get('cache_creation', 0)
            month_sessions += m_data['sessions']

    month_cost = calculate_cost(month_total_in, month_total_out, month_total_cr, month_total_cc)

    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    eom_prediction = (month_cost['total'] / days_elapsed * days_in_month
                      if days_elapsed > 0 else 0)

    result = {
        'session': session_data,
        'today': {
            'input': today_data.get('input', 0),
            'output': today_data.get('output', 0),
            'cache_read': today_data.get('cache_read', 0),
            'cache_creation': today_data.get('cache_creation', 0),
            'total': today_tokens,
            'sessions': today_data.get('sessions', 0),
        },
        'month': {
            'key': this_month,
            'input': month_total_in,
            'output': month_total_out,
            'cache_read': month_total_cr,
            'cache_creation': month_total_cc,
            'total': month_total_in + month_total_out + month_total_cr + month_total_cc,
            'sessions': month_sessions,
            'cost': month_cost,
            'eom_prediction': eom_prediction,
            'days_elapsed': days_elapsed,
            'days_in_month': days_in_month,
        },
        'all_time': {
            'sessions': len(cache['sessions']),
            'total': sum(s['total'] for s in cache['sessions']),
        },
        'updated_at': cache['updated_at'],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    force_update = '--update-cache' in sys.argv or '--force' in sys.argv

    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return

    # 熔断预警检查（SQLite 聚合查询，O(1)）
    run_alerts()

    cache = collect_all_usage(force=force_update)

    if '--json' in sys.argv:
        output_json(cache)
        return

    if '--session' in sys.argv:
        current_file = get_current_session_id()
        if current_file:
            result = parse_transcript(current_file)
            s_date, s_time, s_in, s_out, s_cr, s_cc, s_model = result
            s_total = s_in + s_out + s_cr + s_cc
            s_cost = calculate_cost(s_in, s_out, s_cr, s_cc, s_model)
            print(f'输入: {format_tokens(s_in)}  |  输出: {format_tokens(s_out)}')
            print(f'Cache read: {format_tokens(s_cr)}  |  Cache write: {format_tokens(s_cc)}')
            print(f'合计: {format_tokens(s_total)}')
            print(f'费用: ¥ {s_cost["total"]:.4f}')
            # 持久化当前 session 到 SQLite
            save_session_to_db({
                'session_id': current_file.stem,
                'input_tokens': s_in, 'output_tokens': s_out,
                'cache_read_tokens': s_cr, 'cache_creation_tokens': s_cc,
                'total_tokens': s_total,
                'input_cost': s_cost['input_cost'],
                'output_cost': s_cost['output_cost'],
                'cache_cost': s_cost['cache_cost'],
                'total_cost': s_cost['total'],
                'model': s_cost['model']
            })
        else:
            print('无当前 session 数据')
        return

    if '--today' in sys.argv:
        today_str = date.today().isoformat()
        today_data = cache['daily'].get(today_str, {})
        t_total = (today_data.get('input', 0) + today_data.get('output', 0)
                   + today_data.get('cache_read', 0) + today_data.get('cache_creation', 0))
        print(f'{today_str}: {format_tokens(t_total)}  ({today_data.get("sessions", 0)} sessions)')
        return

    if '--month' in sys.argv:
        this_month = date.today().isoformat()[:7]
        m_in = m_out = m_cr = m_cc = m_sessions = 0
        for m_key, m_data in cache['monthly'].items():
            if m_key == this_month:
                m_in += m_data['input']
                m_out += m_data['output']
                m_cr += m_data.get('cache_read', 0)
                m_cc += m_data.get('cache_creation', 0)
                m_sessions += m_data['sessions']
        m_total = m_in + m_out + m_cr + m_cc
        m_cost = calculate_cost(m_in, m_out, m_cr, m_cc)
        print(f'{this_month}: {format_tokens(m_total)}  ({m_sessions} sessions)')
        print(f'费用: ¥ {m_cost["total"]:.2f}')
        return

    detail = '--detail' in sys.argv
    display_full(cache, detail=detail)

    # 持久化当前 session 到 SQLite
    current_file = get_current_session_id()
    if current_file:
        result = parse_transcript(current_file)
        s_date, s_time, s_in, s_out, s_cr, s_cc, s_model = result
        if s_in + s_out + s_cr + s_cc > 0:
            s_cost = calculate_cost(s_in, s_out, s_cr, s_cc, s_model)
            save_session_to_db({
                'session_id': current_file.stem,
                'input_tokens': s_in, 'output_tokens': s_out,
                'cache_read_tokens': s_cr, 'cache_creation_tokens': s_cc,
                'total_tokens': s_in + s_out + s_cr + s_cc,
                'input_cost': s_cost['input_cost'],
                'output_cost': s_cost['output_cost'],
                'cache_cost': s_cost['cache_cost'],
                'total_cost': s_cost['total'],
                'model': s_cost['model']
            })


if __name__ == '__main__':
    main()
